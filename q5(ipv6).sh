#!/bin/bash

# Function to validate basic IPv6 address format
validate_ipv6_format() {
    local ipv6="$1"

    # Check for multiple :: sequences
    if [[ $(echo "$ipv6" | grep -o "::" | wc -l) -gt 1 ]]; then
        echo "Error: IPv6 address cannot contain multiple '::' sequences: $ipv6" >&2
        return 1
    fi

    # If there's no ::, check for exactly 8 blocks
    if [[ "$ipv6" != *"::"* ]]; then
        local block_count=$(echo "$ipv6" | tr ':' ' ' | wc -w)
        if [ "$block_count" -ne 8 ]; then
            echo "Error: IPv6 address without '::' must have exactly 8 blocks: $ipv6" >&2
            return 1
        fi
    fi

    # Check each block for valid hex digits and length
    local blocks=(${ipv6//:/ })
    for block in "${blocks[@]}"; do
        # Skip empty blocks caused by ::
        if [ -z "$block" ]; then
            continue
        fi
        if ! echo "$block" | grep -E '^[0-9a-fA-F]{1,4}$' >/dev/null; then
            echo "Error: Invalid hex block in IPv6 address: $block in $ipv6" >&2
            return 1
        fi
    done

    return 0
}

# Function to expand a compressed IPv6 address to its full form
expand_ipv6() {
    local ipv6="$1"
    local blocks
    local expanded_blocks=()
    local i

    # Step 1: Replace :: with appropriate number of :0000: blocks
    if [[ "$ipv6" == *"::"* ]]; then
        # Count the number of blocks before and after ::
        local before_after=(${ipv6//::/ })
        local before=(${before_after[0]//:/ })
        local after=(${before_after[1]//:/ })
        local before_count=${#before[@]}
        local after_count=${#after[@]}
        local zero_blocks=$((8 - before_count - after_count))

        # Validate the number of blocks
        if [ "$zero_blocks" -lt 0 ]; then
            echo "Error: Too many blocks in compressed IPv6 address: $ipv6" >&2
            return 1
        fi

        # Build the expanded address
        local temp_blocks=()
        for ((i=0; i<before_count; i++)); do
            temp_blocks+=("${before[i]}")
        done
        for ((i=0; i<zero_blocks; i++)); do
            temp_blocks+=("0000")
        done
        for ((i=0; i<after_count; i++)); do
            temp_blocks+=("${after[i]}")
        done
        blocks=("${temp_blocks[@]}")
    else
        blocks=(${ipv6//:/ })
    fi

    # Validate the number of blocks
    if [ ${#blocks[@]} -ne 8 ]; then
        echo "Error: IPv6 address must have exactly 8 blocks after expansion: $ipv6" >&2
        return 1
    fi

    # Step 2: Expand each block to 4 hex digits by padding with leading zeros
    for ((i=0; i<8; i++)); do
        local block="${blocks[i]}"
        # Validate block contains only hex digits (redundant but kept for safety)
        if ! echo "$block" | grep -E '^[0-9a-fA-F]{1,4}$' >/dev/null; then
            echo "Error: Invalid hex block in IPv6 address: $block in $ipv6" >&2
            return 1
        fi
        # Convert to lowercase for consistency
        block=$(echo "$block" | tr '[:upper:]' '[:lower:]')
        # Pad with leading zeros to make 4 digits
        while [ ${#block} -lt 4 ]; do
            block="0$block"
        done
        expanded_blocks[i]="$block"
    done

    # Step 3: Join the blocks with colons
    local expanded=$(IFS=:; echo "${expanded_blocks[*]}")
    echo "$expanded"
}

# Function to validate an IPv6 address and return its expanded form
validate_ipv6() {
    local ipv6="$1"
    local expanded

    # First, validate the basic format
    if ! validate_ipv6_format "$ipv6"; then
        return 1
    fi

    # Expand the address
    if ! expanded=$(expand_ipv6 "$ipv6"); then
        return 1
    fi

    # Validate the expanded address: 8 groups of 4 hex digits, separated by colons
    if ! echo "$expanded" | grep -E '^([0-9a-f]{4}:){7}[0-9a-f]{4}$' >/dev/null; then
        echo "Error: Invalid IPv6 address: $ipv6 (expanded: $expanded)" >&2
        return 1
    fi
    echo "$expanded"
}

# Function to compute the network address (manual calculation)
get_network() {
    local expanded_ipv6="$1"  # Use the pre-expanded address
    local prefix="$2"
    
    if [ "$prefix" -lt 0 ] || [ "$prefix" -gt 128 ]; then
        echo "Error: Invalid prefix: $prefix (must be between 0 and 128)" >&2
        return 1
    fi

    local blocks=($(echo "$expanded_ipv6" | tr ':' ' '))
    local network=""
    local i
    for i in $(seq 0 7); do
        if [ $((i * 16)) -lt "$prefix" ]; then
            network+="${blocks[i]}"
        else
            network+="0000"
        fi
        [ "$i" -lt 7 ] && network+=":"
    done
    echo "$network"
}

# Function to compare two IPv6 addresses based on the subnet prefix
ipv6_compare_subnet() {
    local ipv6_1="$1"
    local prefix_1="$2"
    local ipv6_2="$3"
    local prefix_2="$4"

    # Validate and expand both addresses
    local expanded_1
    if ! expanded_1=$(validate_ipv6 "$ipv6_1"); then
        exit 1
    fi
    local expanded_2
    if ! expanded_2=$(validate_ipv6 "$ipv6_2"); then
        exit 1
    fi

    # Use the smaller prefix for comparison
    local prefix
    if [ "$prefix_1" -lt "$prefix_2" ]; then
        prefix="$prefix_1"
        echo "Using prefix /$prefix from first address (smaller prefix) for comparison."
    else
        prefix="$prefix_2"
        echo "Using prefix /$prefix from second address (smaller prefix) for comparison."
    fi

    # Calculate network addresses using the pre-expanded addresses
    local network_1
    if ! network_1=$(get_network "$expanded_1" "$prefix"); then
        exit 1
    fi
    local network_2
    if ! network_2=$(get_network "$expanded_2" "$prefix"); then
        exit 1
    fi

    echo "Comparing IPv6 addresses based on prefix /$prefix:"
    echo "Network of $ipv6_1: $network_1"
    echo "Network of $ipv6_2: $network_2"
    if [ "$network_1" == "$network_2" ]; then
        echo "The two IPv6 addresses are on the same subnet."
    else
        echo "The two IPv6 addresses are not on the same subnet."
    fi
}

# Main script
read -p "Enter the 1st IPv6 address with prefix (e.g., 2001:db8::1/64): " input_1
read -p "Enter the 2nd IPv6 address with prefix (e.g., 2001:db8::2/64): " input_2

IFS='/' read -r ipv6_1 prefix_1 <<< "$input_1"
IFS='/' read -r ipv6_2 prefix_2 <<< "$input_2"

prefix_1=${prefix_1:-64}
prefix_2=${prefix_2:-64}

ipv6_compare_subnet "$ipv6_1" "$prefix_1" "$ipv6_2" "$prefix_2"