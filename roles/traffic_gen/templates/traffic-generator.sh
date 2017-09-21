#!/bin/bash
cd "$HOME" || exit
 
function send_and_receive {
	nc -u -l "{{traffic_gen_port}}" > /dev/null &
	while true; do
		nc -u "$1" "{{traffic_gen_port}}" < /dev/urandom
		sleep 1
	done
}

# {% if 'gateway' in group_names %}

send_and_receive "{{client_mesh_ip}}"

# {% elif  'client' in group_names %}

send_and_receive "{{gateway_mesh_ip}}"

# {% endif %}
