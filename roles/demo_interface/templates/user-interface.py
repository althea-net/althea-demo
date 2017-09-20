#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import subprocess
import socket
import json
import Adafruit_CharLCD as LCD
from procfs import Proc

NAME = "{{name}}"
MESH_IP = "{{mesh_ip}}"
HOSTNAME = "{{inventory_hostname}}"
STAT_SERVER = "http://{{gateway_ip}}:{{stat_server_port}}"

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072
# Used in place of tunnel negotiation
GATEWAY_IP = "10.28.7.7"

GLOBAL_VARS = {
    "last_message": "",
    "last_total_bytes": 0,
    "total_earnings": 0
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


def get_dump():
    """Get babel's dump"""
    bsock.sendall('dump\n')
    table_lines = bsock.recv(BABEL_BUFF).split('\n')
    while not is_end_string(table_lines[-2]):
        table_lines.extend(bsock.recv(BABEL_BUFF).split('\n'))
    return table_lines


def message_both(message):
    """Display a message on screen and in terminal"""
    print message
    if GLOBAL_VARS["last_message"] != message:
        lcd.clear()
        lcd.message(message)
    GLOBAL_VARS["last_message"] = message


def get_our_price():
    """Get our current price from babel"""
    table_lines = get_dump()
    assert(is_end_string(table_lines[-2]))
    for table_line in table_lines:
        if 'local' in table_line and 'price' in table_line:
            if int(grab_babel_val(table_line, 'price')) is None:
                print(table_line)
            return int(grab_babel_val(table_line, 'price'))


def set_our_price(price):
    """Set our current price on babel"""
    bsock.sendall('price {}\n'.format(price))
    print bsock.recv(BABEL_BUFF)


def is_end_string(message):
    """Identifies babel message end strings"""
    # ok, no, bad are the only options
    if len(message) > 3:
        return False
    elif 'ok' in message or 'no' in message or 'bad' in message:
        return True
    else:
        return False


def grab_babel_val(message, val):
    """Extract given value from babel output"""
    message = message.split(" ")
    for idx, item in enumerate(message):
        if val.lower() in item.lower():
            if message[idx + 1] is None:
                break
            return message[idx + 1]
    print("Looking for {} in {}".format(val, message))
    raise ValueError("Babel comm error")


def to_cash(num_bytes, price):
    """Get cost for bytes at price"""
    return (float(num_bytes) / 1000000000) * price


def get_total_forwarded():
    """Find out how much data the node has forwarded"""
    return int(run_cmd("iptables -L -n -v -x | awk '/FORWARD/ { print $7; }'")['stdout'])


def get_current_bytes():
    """How many more bytes have been forwarded since we last checked"""
    total_bytes = get_total_forwarded()
    current_bytes = total_bytes - GLOBAL_VARS["last_total_bytes"]
    GLOBAL_VARS["last_total_bytes"] = total_bytes
    return current_bytes


def json_post_cmd(data, dest):
    message = 'curl -d \'{}\' -H "Content-Type: application/json" -X POST {}'.format(
        json.dumps(data), dest)
    return message


# def update_earnings_info(current_bytes, current_earnings, current_price):
#     """Put the earnings on the screen, and send to stat server"""
#     current_kbs = current_bytes / 1000
#     message = "{:.0f}kbs +${:.2f}\nTotal: ${:.2f}".format(
#         current_kbs, current_earnings, GLOBAL_VARS["total_earnings"])
#     message_both(message)

#     return datetime.datetime.utcnow(), message

def update_earnings_info(message, current_price):
    message_both(message)
    cmd = json_post_cmd({"id": NAME, "message": message, "price": current_price,
                         "total": GLOBAL_VARS["total_earnings"]}, STAT_SERVER)
    run_cmd_nowait(cmd)
    return datetime.datetime.utcnow(), message


def active_earnings_message(current_bytes, current_earnings):
    current_kbs = current_bytes / 1000
    return "{:.0f}kbs +${:.2f}\nTotal: ${:.2f}".format(
        current_kbs, current_earnings, GLOBAL_VARS["total_earnings"])


def inactive_earnings_message():
    return "0kbs\nTotal: ${:.2f}".format(
        GLOBAL_VARS["total_earnings"])


def view_earnings():
    """Main screen"""
    last_update = datetime.datetime.utcnow()
    current_price = get_our_price()
    price_step = 10
    while True:
        if lcd.is_pressed(LCD.UP):
            current_price = max(current_price + int(1 * (price_step / 10)), 0)
            set_our_price(current_price)
            price_step = max(price_step * 1.3, 500)
            message_both("Cents per GB:\n{}".format(current_price))

            time.sleep(1)
            current_price = get_our_price()
        elif lcd.is_pressed(LCD.DOWN):
            current_price = max(current_price - int(1 * (price_step / 10)), 0)
            set_our_price(current_price)
            price_step = max(price_step * 1.3, 500)
            message_both("Cents per GB:\n{}".format(current_price))

            time.sleep(1)
            current_price = get_our_price()
        elif lcd.is_pressed(LCD.LEFT):
            message_both("{}\n{}".format(MESH_IP, HOSTNAME))
            time.sleep(2)
        elif lcd.is_pressed(LCD.RIGHT):
            message_both("Name:\n{}".format(NAME))
            time.sleep(2)
        else:
            price_step = max(price_step / 2, 10)
            now = datetime.datetime.utcnow()
            if now - last_update > datetime.timedelta(seconds=1):
                current_bytes = get_current_bytes()

                if current_bytes > 0:
                    current_earnings = to_cash(current_bytes, get_our_price())
                    message = active_earnings_message(
                        current_bytes, current_earnings)
                    GLOBAL_VARS["total_earnings"] = GLOBAL_VARS["total_earnings"] + \
                        current_earnings
                else:
                    message = inactive_earnings_message()

                update_earnings_info(message, current_price)
                last_update = datetime.datetime.utcnow()


lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()

bsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to\nBabel...')
bsock.connect((BABEL_IP, BABEL_PORT))
print bsock.recv(BABEL_BUFF)
message_both('Connected to\nBabel!')

message_both('intermediary')
view_earnings()
