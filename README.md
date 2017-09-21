Althea Demo
===========

A quick and safe (no money involved) way to demonstrate incentivized mesh on some single board computers.

SBC's like the RPI aren't really useful for mesh routing, dedicated routing devices in the same price range
blow it out of the water by a factor of ten in routing performance, but they don't have the IO for a cool
screen and some buttons.

To Run
======

Install raspbian on your pi, specifically a jessie image since ad-hoc mode
is broken in stretch as of this writing. If it's been a long time since the commit
date on this file maybe try it again. I find this image works well

   http://downloads.raspberrypi.org/raspbian_lite/images/raspbian_lite-2017-06-23/

Put the image onto the sdcard then mount the /boot partition and create a emtpy
file called 'ssh' this will enable ssh login on first boot. Which is insecure but
the installation script will install your public rsa key and disable password login

To find your pis `sudo nmap -sP -PS22,3389 192.168.1.1/24`

then create a file called `hosts` containing the following

```
[intermediary]
192.168.1.106 name=Lumpkin mesh_ip=10.28.7.2
192.168.1.119 name=Ada mesh_ip=10.28.7.3
192.168.1.219 name=Franklin mesh_ip=10.28.7.1
[client]
192.168.1.152 mesh_ip=10.28.7.6
[gateway]
192.168.1.233 mesh_ip=10.28.7.7
```

The gateway will be the network exit, you can have more than one, but do more than one
provisioning run, intermediaries just pass traffic and make money, clients send data
to the gateway and spend money. You can have as many of either as you want just remember
that clients will target the gateway for the run during which they where provisioned
(since autonegotiation isn't done yet)

Finally run

    ansible-playbook -i hosts setup-demo.yml --ask-pass


You should find yourself with a rpi running Althea

TODO
====

Link to Adafruit parts and guide
