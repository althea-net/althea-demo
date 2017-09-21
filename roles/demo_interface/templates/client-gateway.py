#!/usr/bin/python
"""Runs user interface for gateway and client nodes"""
from common import message_both, run_cmd


def get_total_sent():
    """Find out how much data the node has sent"""
    return int(run_cmd("iptables -L -n -v -x | awk '/FORWARD/ { print $7; }'")['stdout'])
