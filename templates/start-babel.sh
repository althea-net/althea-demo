#!/bin/bash
set -eux
sleep 10
ifconfig wlan0 up
iwconfig wlan0 mode ad-hoc
iwconfig wlan0 essid "Althea-demo"
iwconfig wlan0 channel 4
ifconfig wlan0 10.28.{{ 254 | random }}.{{ 254 | random }} netmask 255.255.255.0
babeld -d 1 -P 1024 -G 8080 -w wlan0
