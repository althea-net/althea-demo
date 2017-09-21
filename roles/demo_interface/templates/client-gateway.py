#!/usr/bin/python
"""Runs user interface for gateway and client nodes"""

import datetime
from common import message_both, run_cmd
import Adafruit_CharLCD as lcd


def get_total_sent():
    """Find out how much data the node has sent"""
    return int(run_cmd("iptables -L -n -v -x | awk '/OUTPUT/ { print $7; }'")['stdout'])


def get_total_received():
    """Find out how much data the node has received"""
    return int(run_cmd("iptables -L -n -v -x | awk '/INPUT/ { print $7; }'")['stdout'])


def update_traffic_info(message):
    """send and display traffic update"""
    message_both(message, LCD)
    return datetime.datetime.utcnow(), message


def traffic_message(sent_bytes, received_bytes):
    """generate traffic message"""
    sent_kbs = sent_bytes / 1000
    received_kbs = received_bytes / 1000
    return "Out: {:.0f}kb/s\nIn: {:.0f}kb/s".format(sent_kbs, received_kbs)


def view_traffic():
    """Display traffic interface"""
    last_update = datetime.datetime.utcnow()
    last_total_sent = get_total_sent()
    last_total_received = get_total_received()
    while True:
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=1):
            total_sent = get_total_sent()
            total_received = get_total_received()
            current_sent = total_sent - last_total_sent
            current_received = total_received - last_total_received
            message = traffic_message(current_sent, current_received)
            update_traffic_info(message)
            last_update = datetime.datetime.utcnow()
            last_total_sent = total_sent
            last_total_received = total_received


LCD = lcd.Adafruit_CharLCDPlate()
view_traffic()
