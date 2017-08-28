#!/bin/bash

# A quick script to make flashing a lot of sdcards fast

set -eux
IMAGE=
DEVICE=mmcblk0
MOUNTPOINT=/tmp/mount
PARTITION="p1"

while true
do
	while [ ! -e "/dev/$DEVICE" ]
	do
		sleep 1
	done
	dd bs=65536 if=$IMAGE of=/dev/$DEVICE
	mkdir -p $MOUNTPOINT
	mount /dev/$DEVICE$PARTITION $MOUNTPOINT/
	touch $MOUNTPOINT/ssh
	umount $MOUNTPOINT/
	read -p "SD card flashed, press key for next" -n1 -s
done
