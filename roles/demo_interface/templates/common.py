#!/usr/bin/python
"""Shared functionality for all nodes"""

import subprocess
import json

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072

GLOBAL_VARS = {
    "last_message": ""
}


def run_cmd(cmd):
    """Run a command in the shell"""
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    out = {}
    out['stdout'] = stdout.strip()
    out['stderr'] = stderr.strip()
    out['rc'] = process.returncode
    return out


def run_cmd_nowait(cmd):
    """Run a command without waiting"""
    subprocess.Popen(cmd, shell=True,
                     stdin=None, stdout=None, stderr=None, close_fds=True)


def message_both(message, LCD):
    """Display a message on screen and in terminal"""
    print message
    if GLOBAL_VARS["last_message"] != message:
        LCD.clear()
        LCD.message(message)
    GLOBAL_VARS["last_message"] = message


def json_post_cmd(data, dest):
    message = 'curl -d \'{}\' -H "Content-Type: application/json" -X POST {}'.format(
        json.dumps(data), dest)
    return message
