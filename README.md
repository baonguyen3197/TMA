## --- Q2 --- ##
Convert string:  Xuyen -> enuXy using Python

    python ./q2.py

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

## --- Q3 --- ##
# run Login Application

    cd test/
    python ./q3.py

# -------------------------------------------------------------------------- #

# run test
    pytest --cov=q3 --cov-report=term-missing

                    test session starts 
platform win32 -- Python 3.13.2, pytest-8.3.5, pluggy-1.5.0
rootdir: D:\TMA
plugins: cov-6.0.0
collected 40 items                                                                                                                    
test\test_q3.py ........................................................ [100%]

coverage: platform win32, python 3.13.2-final-0
Name         Stmts   Miss  Cover   Missing
------------------------------------------
test\q3.py     144      1    99%   226
------------------------------------------
TOTAL          144      1    99%

40 passed in 0.73s 

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

## --- Q4 --- ##
Write a program to revert input string to output like below:
		input: 	'Automation'
		output: 'oitamotuAn'

    python ./q4.py

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

## --- Q5 --- ##
Shell script compare network subnet of ipv4 & ipv6
	2001::1
	2001:2::2

# Run on WSL

    wsl.exe -d Ubuntu --user nhqb

# Run script

    ./q5(ipv4).sh
    ./q5(ipv6).sh

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

## --- sipcalc usage --- ##
## --- ipv6 --- ##

sipcalc 2001:db8::fd12:7890/64
sipcalc 2001:db8::2/64

-[ipv6 : 2001:db8::fd12:7890/64] - 0

[IPV6 INFO]
Expanded Address        - 2001:0db8:0000:0000:0000:0000:fd12:7890
Compressed address      - 2001:db8::fd12:7890
Subnet prefix (masked)  - 2001:db8:0:0:0:0:0:0/64
Address ID (masked)     - 0:0:0:0:0:0:fd12:7890/64
Prefix address          - ffff:ffff:ffff:ffff:0:0:0:0
Prefix length           - 64
Address type            - Aggregatable Global Unicast Addresses
Network range           - 2001:0db8:0000:0000:0000:0000:0000:0000 -
                          2001:0db8:0000:0000:ffff:ffff:ffff:ffff

-
-[ipv6 : 2001:db8::2/64] - 0

[IPV6 INFO]
Expanded Address        - 2001:0db8:0000:0000:0000:0000:0000:0002
Compressed address      - 2001:db8::2
Subnet prefix (masked)  - 2001:db8:0:0:0:0:0:0/64
Address ID (masked)     - 0:0:0:0:0:0:0:2/64
Prefix address          - ffff:ffff:ffff:ffff:0:0:0:0
Prefix length           - 64
Address type            - Aggregatable Global Unicast Addresses
Network range           - 2001:0db8:0000:0000:0000:0000:0000:0000 -
                          2001:0db8:0000:0000:ffff:ffff:ffff:ffff

-

# -------------------------------------------------------------------------- #
## --- ipv4 --- ##

sipcalc 1.2.3.4/8
-[ipv4 : 1.2.3.4/8] - 0

[CIDR]
Host address            - 1.2.3.4
Host address (decimal)  - 16909060
Host address (hex)      - 1020304
Network address         - 1.0.0.0
Network mask            - 255.0.0.0
Network mask (bits)     - 8
Network mask (hex)      - FF000000
Broadcast address       - 1.255.255.255
Cisco wildcard          - 0.255.255.255
Addresses in network    - 16777216
Network range           - 1.0.0.0 - 1.255.255.255
Usable range            - 1.0.0.1 - 1.255.255.254

-

sipcalc 1.2.5.6/8
-[ipv4 : 1.2.5.6/8] - 0

[CIDR]
Host address            - 1.2.5.6
Host address (decimal)  - 16909574
Host address (hex)      - 1020506
Network address         - 1.0.0.0
Network mask            - 255.0.0.0
Network mask (bits)     - 8
Network mask (hex)      - FF000000
Broadcast address       - 1.255.255.255
Cisco wildcard          - 0.255.255.255
Addresses in network    - 16777216
Network range           - 1.0.0.0 - 1.255.255.255
Usable range            - 1.0.0.1 - 1.255.255.254

-

# -------------------------------------------------------------------------- #

sipcalc 1.2.3.4/16
-[ipv4 : 1.2.3.4/16] - 0

[CIDR]
Host address            - 1.2.3.4
Host address (decimal)  - 16909060
Host address (hex)      - 1020304
Network address         - 1.2.0.0
Network mask            - 255.255.0.0
Network mask (bits)     - 16
Network mask (hex)      - FFFF0000
Broadcast address       - 1.2.255.255
Cisco wildcard          - 0.0.255.255
Addresses in network    - 65536
Network range           - 1.2.0.0 - 1.2.255.255
Usable range            - 1.2.0.1 - 1.2.255.254

-

sipcalc 1.2.5.6/16
-[ipv4 : 1.2.5.6/16] - 0

[CIDR]
Host address            - 1.2.5.6
Host address (decimal)  - 16909574
Host address (hex)      - 1020506
Network address         - 1.2.0.0
Network mask            - 255.255.0.0
Network mask (bits)     - 16
Network mask (hex)      - FFFF0000
Broadcast address       - 1.2.255.255
Cisco wildcard          - 0.0.255.255
Addresses in network    - 65536
Network range           - 1.2.0.0 - 1.2.255.255
Usable range            - 1.2.0.1 - 1.2.255.254

-

# -------------------------------------------------------------------------- #

sipcalc 1.2.3.4/24
-[ipv4 : 1.2.3.4/24] - 0

[CIDR]
Host address            - 1.2.3.4
Host address (decimal)  - 16909060
Host address (hex)      - 1020304
Network address         - 1.2.3.0
Network mask            - 255.255.255.0
Network mask (bits)     - 24
Network mask (hex)      - FFFFFF00
Broadcast address       - 1.2.3.255
Cisco wildcard          - 0.0.0.255
Addresses in network    - 256
Network range           - 1.2.3.0 - 1.2.3.255
Usable range            - 1.2.3.1 - 1.2.3.254

-

sipcalc 1.2.5.6/24
-[ipv4 : 1.2.5.6/24] - 0

[CIDR]
Host address            - 1.2.5.6
Host address (decimal)  - 16909574
Host address (hex)      - 1020506
Network address         - 1.2.5.0
Network mask            - 255.255.255.0
Network mask (bits)     - 24
Network mask (hex)      - FFFFFF00
Broadcast address       - 1.2.5.255
Cisco wildcard          - 0.0.0.255
Addresses in network    - 256
Network range           - 1.2.5.0 - 1.2.5.255
Usable range            - 1.2.5.1 - 1.2.5.254

-

