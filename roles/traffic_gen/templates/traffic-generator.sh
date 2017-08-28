#!/bin/bash
{% if devel %}
while true; do
	ping 8.8.8.8
done
{% else %}
cd $HOME
dd if=/dev/urandom of=out.file count=10000
while true; do
	scp -o StrictHostKeyChecking=no out.file pi@{{gateway_ip}}:out.file
done
{% endif %}
