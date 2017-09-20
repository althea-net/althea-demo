#!/bin/bash
rm /var/run/babeld.pid
set -eux
# wlan config
ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "Althea-demo"
iwconfig wlan0 channel {{channel}}
iwconfig wlan0 txpower {{tx_power}}

# gateway has a static external ip, everyone else is randomized
{% if 'gateway' in group_names %}
set +eux
ip a add {{gateway_ip}}/16 dev wlan0
set -eux
{% elif 'client' in group_names %}
set +eux
ip a add {{client_ip}}/16 dev wlan0
set -eux
{% else %}
set +eux
ip a add {{mesh_ip}}/16 dev wlan0
set -eux
{% endif %}


# Run babel with a price of 1024, a management server on 8080, on the wireguard
# and wlan interfaces with a hello period of 1 only advertising routes on wlan0
babeld -d 1 -h 1 -P 1024 -G 8080 -w wlan0 \
-C "in if wg0 deny" \
{% if 'client' in group_names %}
{% for gateway in groups['gateway'] %}
-C "in neigh {{hostvars[gateway]['ansible_wlan0']['ipv6'][0]['address']}} deny" \
{% endfor %}
{% endif %}
-C 'redistribute local if wlan0' -C 'redistribute local deny'
