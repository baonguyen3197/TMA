# #!/bin/bash

# ipv4_check() {
#     local ipv4="$1"
#     local mask="$2"

#     IFS='.' read -r -a octets <<< "$ipv4"

#     if [ "${#octets[@]}" -ne 4 ]; then
#         # echo "Invalid IPv4 address: $ipv4"
#         return 1
#     fi

#     for octet in "${octets[@]}"; do
#         if ! [[ "$octet" =~ ^[0-9]+$ ]]; then
#             # echo "Invalid IPv4 address: $ipv4"
#             return 1
#         fi

#         if [ "$octet" -lt 0 ] || [ "$octet" -gt 255 ]; then
#             # echo "Invalid IPv4 address: $ipv4"
#             return 1
#         fi
#     done

#     local network_address="${octets[0]}.${octets[1]}.${octets[2]}.${octets[3]}"

#     return 0
# }

# ipv4_compare() {
#     local ipv4_1="$1"
#     local ipv4_2="$2"

#     IFS='.' read -r -a octets_1 <<< "$ipv4_1"
#     IFS='.' read -r -a octets_2 <<< "$ipv4_2"

#     if ! ipv4_check "$ipv4_1"; then
#         echo "Error: Invalid 1st IPv4 address: $ipv4_1"
#         exit 1
#     fi
    
#     if ! ipv4_check "$ipv4_2"; then
#         echo "Error: Invalid 2nd IPv4 address: $ipv4_2"
#         exit 1
#     fi

#     for i in {0..2}; do
#         echo "${octets_1[i]}" compared to "${octets_2[i]}"
#         if [ "${octets_1[i]}" -ne "${octets_2[i]}" ]; then
#             echo "${octets_1[i]}" is not equal to "${octets_2[i]}"
#             echo "The two IPv4 addresses are not on the same network"
#             return
#         fi
#     done

#     echo "The two IPv4 addresses are on the same network"
# }

# read -p "Enter the 1st IPv4 address: " ipv4_1
# read -p "Enter the 2nd IPv4 address: " ipv4_2

# ipv4_compare "$ipv4_1" "$ipv4_2"

# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////

# Compare with mask

#!/bin/bash

ipv4_check() {
    local ipv4="$1"
    # local mask="$2"

    IFS='.' read -r -a octets <<< "$ipv4"

    if [ "${#octets[@]}" -ne 4 ]; then
        # echo "Invalid IPv4 address: $ipv4"
        return 1
    fi

    for octet in "${octets[@]}"; do
        if ! [[ "$octet" =~ ^[0-9]+$ ]]; then
            # echo "Invalid IPv4 address: $ipv4"
            return 1
        fi

        if [ "$octet" -lt 0 ] || [ "$octet" -gt 255 ]; then
            # echo "Invalid IPv4 address: $ipv4"
            return 1
        fi
    done

    if [ -n "$mask" ]; then
        if ! [[ "$mask" =~ ^[0-9]+$ ]]; then
            echo "Invalid subnet mask"
            return 1
        fi

        if [ "$mask" -lt 0 ] || [ "$mask" -gt 32 ]; then
            # echo "Invalid subnet mask"
            return 1
        fi
    fi

    local network_address=$((octets[0] & m1)).$((octets[1] & m2)).$((octets[2] & m3)).$((octets[3] & m4))

    return 0
}

calculate_network_address() {
    local ipv4="$1"
    local mask="$2"

    IFS='.' read -r -a octets <<< "$ipv4"

    local subnet_mask=$((0xFFFFFFFF << (32 - mask) & 0xFFFFFFFF))
    local m1=$(( (subnet_mask >> 24) & 255 ))
    local m2=$(( (subnet_mask >> 16) & 255 ))
    local m3=$(( (subnet_mask >> 8) & 255 ))
    local m4=$(( subnet_mask & 255 ))

    echo "Subnet mask octets: m1=$m1, m2=$m2, m3=$m3, m4=$m4"

    # Calculate the network address
    local n1=$((octets[0] & m1))
    local n2=$((octets[1] & m2))
    local n3=$((octets[2] & m3))
    local n4=$((octets[3] & m4))

    echo "Network address octets: n1=$n1, n2=$n2, n3=$n3, n4=$n4"

    echo "$n1.$n2.$n3.$n4"
}

# calculate_network_address "1.18.14.53" "27"

ipv4_compare() {
    local ipv4_1="$1"
    local mask_1="$2"
    local ipv4_2="$3"
    local mask_2="$4"

    if ! ipv4_check "$ipv4_1" "$mask_1"; then
        echo "Error: Invalid 1st IPv4 address or mask: $ipv4_1/$mask_1"
        exit 1
    fi
    
    if ! ipv4_check "$ipv4_2" "$mask_2"; then
        echo "Error: Invalid 2nd IPv4 address or mask: $ipv4_2/$mask_2"
        exit 1
    fi

    local network_address_1="$(calculate_network_address "$ipv4_1" "$mask_1")"
    local network_address_2="$(calculate_network_address "$ipv4_2" "$mask_2")"

    if [ "$network_address_1" != "$network_address_2" ]; then
        echo "The two IPv4 addresses are not on the same network"
        return
    fi

    echo "The two IPv4 addresses are on the same network"
}

read -p "Enter the 1st IPv4 address with subnet mask (e.g., 192.168.1.1/24): " input_1
read -p "Enter the 2nd IPv4 address with subnet mask (e.g., 192.168.1.2/24): " input_2

IFS='/' read -r ipv4_1 mask_1 <<< "$input_1"
IFS='/' read -r ipv4_2 mask_2 <<< "$input_2"

ipv4_compare "$ipv4_1" "$mask_1" "$ipv4_2" "$mask_2"
