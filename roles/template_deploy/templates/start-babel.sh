#!/bin/bash
rm /var/run/babeld.pid
set -eux
ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "Althea-demo"
iwconfig wlan0 channel {{channel}}
iwconfig wlan0 txpower {{tx_power}}
{% if 'gateway' in group_names %}
set +eux
ip a add {{gateway_ip}}/16 dev wlan0
set -eux
{% else %}
set +eux
ip a add {{generated_ip.stdout}}/16 dev wlan0
set -eux
{% endif %}
{% if devel %}
set +eux
ip link add dev wg0 type wireguard
ip address add dev wg0 {{generatedv6_ip.stdout}}/128
ip -6 a add fe80::/64 dev wg0
wg setconf wg0 /home/pi/wg.conf
ip link set up dev wg0
set -eux
{% endif %}
{% if 'client' in group_names %}
set +eux
route del default
set -eux
ip route add default via {{gateway_ip}} dev wlan0
{% endif %}
{% if 'gateway' in group_names %}
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -i eth0 -o wlan0 -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i wlan0 -o eth0 -j ACCEPT
{% endif %}
babeld -d 1 -h 1 -P 1024 -G 8080 -w wlan0 {% if devel %}wg0{% endif %} \
-C 'redistribute local if wlan0' -C 'redistribute local deny'
