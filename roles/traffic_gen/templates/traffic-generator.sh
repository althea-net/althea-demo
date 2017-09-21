#!/bin/bash

function send_and_receive {
	while true; do
		sendip -p ipv4 -is "$1" -p udp -us "{{traffic_gen_port}}" -ud "{{traffic_gen_port}}" -d r2048 "$2"
	done
}

# {% if 'gateway' in group_names %}

send_and_receive "{{gateway_mesh_ip}}" "{{client_mesh_ip}}" 

# {% elif  'client' in group_names %}

send_and_receive "{{client_mesh_ip}}" "{{gateway_mesh_ip}}"

# {% endif %}
