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

then create a file called `hosts` containing the following

    [pi]
    <list of rpi ip's>

Finally run

    ansible-playbook -i hosts setup-py.yml --ask-pass


You should find yourself with a rpi running Althea

TODO
====

Link to Adafruit parts and guide
