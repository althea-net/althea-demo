#!/bin/bash
pushd $HOME
{% if 'gateway' in group_names %}
while true; do
	nc -u -l 7777 > junk.file
done
{% elif  'client' in group_names %}
dd if=/dev/urandom of=out.file count=10000
while true; do
	cat out.file | nc -u {{gateway_ip}} 7777
done
{% endif %}
