#!/bin/bash
# A quick script to make flashing a lot of sdcards fast

IMAGE=
DEVICE=

while true
do
	while [ ! -e "/dev/$DEVICE" ]
	do
	sleep 1
	done
	dd bs=65536 if=$IMAGE of=/dev/$DEVICE
	mkdir -p mountpoint
	mount /dev/$DEVICEp1 mountpoint/
	touch mountpoint/ssh
	umount mountpoint/
	read -p "SD card flashed, press key for next" -n1 -s
done
