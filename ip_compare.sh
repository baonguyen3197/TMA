# ipv4
ipv4_check() {
    local ipv4="$1"

    IFS='.' read -r -a octets <<< "$ipv4"

    if [ "${#octets[@]}" -ne 4 ]; then
        return 1
    fi

    for octet in "${octets[@]}"; do
        if ! [[ "$octet" =~ ^[0-9]+$ ]]; then
            return 1
        fi

        if [ "$octet" -lt 0 ] || [ "$octet" -gt 255 ]; then
            return 1
        fi
    done

    return 0
}

ipv4_compare() {
    local ipv4_1="$1"
    local ipv4_2="$2"

    IFS='.' read -r -a octets_1 <<< "$ipv4_1"
    IFS='.' read -r -a octets_2 <<< "$ipv4_2"

    if ! ipv4_check "$ipv4_1"; then
        echo "Error: Invalid 1st IPv4 address: $ipv4_1"
        exit 1
    fi

    if ! ipv4_check "$ipv4_2"; then
        echo "Error: Invalid 2nd IPv4 address: $ipv4_2"
        exit 1
    fi

    for i in {0..3}; do
        binary_1=$(printf "%08d" $(echo "obase=2; ${octets_1[i]}" | bc))
        binary_2=$(printf "%08d" $(echo "obase=2; ${octets_2[i]}" | bc))

        echo $binary_1
        echo $binary_2

        for ((j = 0; j < 8; j++)); do
            bit_1="${binary_1:j:1}"
            bit_2="${binary_2:j:1}"

            echo "$bit_1 compared to $bit_2"
            if [ "$bit_1" -ne "$bit_2" ]; then
                echo "The two IPv4 addresses are not identical"
                return
            fi
        done
    done

    echo "The two IPv4 addresses are the same"
}


# ipv6
ipv6_check() {
    local ipv6="$1"

    if [[ $(echo "$ipv6" | grep -o "::" | wc -l) -gt 1 ]]; then
        echo "Error: IPv6 address cannot contain multiple '::' sequences: $ipv6" >&2
        return 1
    fi

    if [[ "$ipv6" != *"::"* ]]; then
        local block_count=$(echo "$ipv6" | tr ':' ' ' | wc -w)
        if [ "$block_count" -ne 8 ]; then
            echo "Error: IPv6 address without '::' must have exactly 8 blocks: $ipv6" >&2
            return 1
        fi
    fi

    local blocks=(${ipv6//:/ })
    for block in "${blocks[@]}"; do
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

expand_ipv6() {
    local ipv6="$1"
    local blocks
    local expanded_blocks=()
    local i

    if [[ "$ipv6" == *"::"* ]]; then
        local before_after=(${ipv6//::/ })
        local before=(${before_after[0]//:/ })
        local after=(${before_after[1]//:/ })
        local before_count=${#before[@]}
        local after_count=${#after[@]}
        local zero_blocks=$((8 - before_count - after_count))

        if [ "$zero_blocks" -lt 0 ]; then
            echo "Error: Too many blocks in compressed IPv6 address: $ipv6" >&2
            return 1
        fi

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

    if [ ${#blocks[@]} -ne 8 ]; then
        echo "Error: IPv6 address must have exactly 8 blocks after expansion: $ipv6" >&2
        return 1
    fi

    for ((i=0; i<8; i++)); do
        local block="${blocks[i]}"
        if ! echo "$block" | grep -E '^[0-9a-fA-F]{1,4}$' >/dev/null; then
            echo "Error: Invalid hex block in IPv6 address: $block in $ipv6" >&2
            return 1
        fi
        block=$(echo "$block" | tr '[:lower:]' '[:upper:]')  # Convert to uppercase for bc
        while [ ${#block} -lt 4 ]; do
            block="0$block"
        done
        expanded_blocks[i]="$block"
    done

    local expanded=$(IFS=:; echo "${expanded_blocks[*]}")
    echo "$expanded"
}

ipv6_compare() {
    local ipv6_1="$1"
    local ipv6_2="$2"

    local expanded_1
    local expanded_2
    if ! expanded_1=$(expand_ipv6 "$ipv6_1"); then
        echo "Error: Invalid 1st IPv6 address: $ipv6_1"
        exit 1
    fi
    if ! expanded_2=$(expand_ipv6 "$ipv6_2"); then
        echo "Error: Invalid 2nd IPv6 address: $ipv6_2"
        exit 1
    fi

    echo "Expanded 1st IPv6 address: $expanded_1"
    echo "Expanded 2nd IPv6 address: $expanded_2"

    IFS=':' read -r -a hextets_1 <<< "$expanded_1"
    IFS=':' read -r -a hextets_2 <<< "$expanded_2"

    for i in {0..7}; do
        local hex_1=$(echo "${hextets_1[i]}" | tr '[:lower:]' '[:upper:]')
        local hex_2=$(echo "${hextets_2[i]}" | tr '[:lower:]' '[:upper:]')
        
        binary_1=$(bc <<< "obase=2; ibase=16; $hex_1")
        binary_2=$(bc <<< "obase=2; ibase=16; $hex_2")

        if [[ -z "$binary_1" || -z "$binary_2" ]]; then
            echo "Error: Binary conversion failed for hextet $hex_1 or $hex_2" >&2
            exit 1
        fi

        binary_1=$(printf "%016d" "$binary_1")
        binary_2=$(printf "%016d" "$binary_2")

        echo "Binary of ${hextets_1[i]}: $binary_1"
        echo "Binary of ${hextets_2[i]}: $binary_2"

        for ((j = 0; j < 16; j++)); do
            bit_1="${binary_1:j:1}"
            bit_2="${binary_2:j:1}"
            echo "$bit_1 compared to $bit_2"
            if [ "$bit_1" -ne "$bit_2" ]; then
                echo "The two IPv6 addresses are not on the same network"
                return
            fi
        done
    done

    echo "The two IPv6 addresses are on the same network"
}

read -p "Enter the 1st ip: " ip1
read -p "Enter the 2nd ip: " ip2

if [[ "$ip1" =~ ":" && "$ip2" =~ "." ]]; then
    echo "Cannot compare an IPv6 address with an IPv4 address"
    exit 1
elif [[ "$ip1" =~ "." && "$ip2" =~ ":" ]]; then
    echo "Cannot compare an IPv4 address with an IPv6 address"
    exit 1
elif [[ "$ip1" =~ ":" && "$ip2" =~ ":" ]]; then
    ipv6_1="$ip1"
    ipv6_2="$ip2"
    ipv6_compare "$ipv6_1" "$ipv6_2"
elif [[ "$ip1" =~ "." && "$ip2" =~ "." ]]; then
    ipv4_1="$ip1"
    ipv4_2="$ip2"
    ipv4_compare "$ipv4_1" "$ipv4_2"
else
    echo "Cannot compare the two IPs"
    exit 1
fi
