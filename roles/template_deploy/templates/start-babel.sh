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
{% else %}
set +eux
ip a add {{generated_ip.stdout}}/16 dev wlan0
set -eux
{% endif %}

# if devel is enabled setup wireguard
{% if devel %}
set +eux
ip link add dev wg0 type wireguard
# babel for some reason can't assign the link local ipv6 address itself on wg
ip address add dev wg0 {{generatedv6_ip.stdout}}/64
wg setconf wg0 /home/pi/wg.conf
ip link set up dev wg0
set -eux
{% endif %}

# Client, setup add wg ipv4 address and ipv4 default route
{% if 'client' in group_names and devel %}
set +eux
ip a add 10.0.{{ 254 | random }}.{{ 254 | random }}/16 dev wg0
ip route del default
set -eux
ip route add default via {{gateway_internal_ip}} dev wg0
{% endif %}

# Gateway setup, setup nat, add gateway fixed wg internal ip
{% if 'gateway' in group_names and devel %}
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wg0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wg0 -o eth0 -j ACCEPT
ip address add dev wg0 {{gateway_internal_ip}}/16
{% endif %}

# Run babel with a price of 1024, a management server on 8080, on the wireguard
# and wlan interfaces with a hello period of 1 only advertising routes on wlan0
babeld -d 1 -h 1 -P 1024 -G 8080 -w wlan0 {% if devel %}wg0{% endif %} \
-C "in if wg0 deny" \

{% if 'gateway' in group_names %}
  {% for client in groups['client'] %}
    -C "in neigh {{hostvars[client]['ansible_wlan0']['ipv6'][0]['address']}} deny" \
  {% endfor %}
{% elif 'client' in group_names %}
  {% for gateway in groups['gateway'] %}
    -C "in neigh {{hostvars[gateway]['ansible_wlan0']['ipv6'][0]['address']}} deny" \
  {% endfor %}
{% endif %}

-C 'redistribute local if wlan0' -C 'redistribute local deny'
