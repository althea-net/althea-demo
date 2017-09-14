#!/bin/bash
cd $HOME
{% if 'gateway' in group_names %}
while true; do
	nc -u -l 7777 > /dev/null
done
{% elif  'client' in group_names %}
dd if=/dev/urandom of=out.file count=10000
while true; do
	cat /dev/urandom | nc -u 10.28.7.7 7777
	sleep 0.1
done
{% endif %}
