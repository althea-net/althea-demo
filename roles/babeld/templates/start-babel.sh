#!/bin/bash
rm /var/run/babeld.pid
set -eux
# wlan config
ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "Althea-demo"
iwconfig wlan0 channel {{channel}}
iwconfig wlan0 txpower {{tx_power}}

{% if 'intermediary' in group_names %}
set +eux
ip a add {{mesh_ip}}/16 dev wlan0
set -eux
{% endif %}
{% if 'gateway' in group_names %}
set +eux
ip a add {{gateway_mesh_ip}}/16 dev wlan0
set -eux
{% endif %}
{% if 'client' in group_names %}
set +eux
ip a add {{client_mesh_ip}}/16 dev wlan0
set -eux
{% endif %}


babeld -M 0 -d 1 -h 1 -P 100 -G 8080 -w wlan0 \
-C "in if wg0 deny" \
{% if 'client' in group_names %}
{% for gateway in groups['gateway'] %}
-C "in neigh {{hostvars[gateway]['ansible_wlan0']['ipv6'][0]['address']}} deny" \
{% endfor %}
{% endif %}
{% if 'gateway' in group_names %}
{% for client in groups['client'] %}
-C "in neigh {{hostvars[client]['ansible_wlan0']['ipv6'][0]['address']}} deny" \
{% endfor %}
{% endif %}
-C 'redistribute local if wlan0' -C 'redistribute local deny'
