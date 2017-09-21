#!/usr/bin/python
"""Runs user interface for gateway and client nodes"""

import datetime
from common import message_both, run_cmd
import Adafruit_CharLCD as lcd


def get_total_sent():
    """Find out how much data the node has sent"""
    return int(run_cmd("iptables -L -n -v -x | awk '/OUTPUT/ { print $7; }'")['stdout'])


def get_total_received():
    """Find out how much data the node has sent"""
    return int(run_cmd("iptables -L -n -v -x | awk '/INPUT/ { print $7; }'")['stdout'])


def update_traffic_info(message):
    """send and display traffic update"""
    message_both(message, LCD)
    return datetime.datetime.utcnow(), message


def traffic_message(sent_bytes, received_bytes):
    """generate traffic message"""
    sent_kbs = sent_bytes / 1000
    received_kbs = received_bytes / 1000
    return "Sent: {:.0f}kb\nReceived: {:.0f}kb".format(sent_kbs, received_kbs)


def view_traffic():
    """Display traffic interface"""
    last_update = datetime.datetime.utcnow()
    while True:
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=1):
            message = traffic_message(get_total_sent(), get_total_received())
            update_traffic_info(message)
            last_update = datetime.datetime.utcnow()


LCD = lcd.Adafruit_CharLCDPlate()
view_traffic()
