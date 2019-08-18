#!/bin/bash
DEFAULT_GATEWAY=$(ip route list 0/0 | awk '{print $3}')
METADATA_PORT=5000
iptables -t nat -F
iptables -t nat -A OUTPUT -p tcp -d 169.254.169.254 --dport 80 -j DNAT --to-destination ${DEFAULT_GATEWAY}:${METADATA_PORT}
