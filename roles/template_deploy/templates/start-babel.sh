#!/bin/bash
rm /var/run/babeld.pid
set -eux
ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "Althea-demo"
iwconfig wlan0 channel 4
{% if 'gateway' in group_names %}
ifconfig wlan0 {{gateway_ip}} netmask 255.255.255.0
{% else %}
ifconfig wlan0 10.28.{{ 254 | random }}.{{ 254 | random }} netmask 255.255.255.0
{% endif %}
{% if devel %}
ip link add dev wg0 type wireguard
ip address add dev wg0 fe80::2cee:2fff:{{ 999 | random }}:{{ 999 | random }}
wg setconf wg0 /home/pi/wg.conf
ip link set up dev wg0
{% endif %}
babeld -d 1 -P 1024 -G 8080 -w wlan0
