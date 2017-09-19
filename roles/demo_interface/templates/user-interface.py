#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import subprocess
import socket
import Adafruit_CharLCD as LCD
from procfs import Proc

#{% if 'gateway' in group_names %}

GROUP = "gateway"

#{% elif  'client' in group_names %}

GROUP = "client"

#{% else %}

GROUP = "intermediary"
NAME = {{name}}
MESH_IP = {{mesh_ip}}
HOSTNAME = {{inventory_hostname}}

#{% endif %}

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072
# Used in place of tunnel negotiation
GATEWAY_IP = "10.28.7.7"

GLOBAL_VARS = {
    "last_message": "",
    "last_total_bytes": "",
    "total_earnings": ""
}


def run_cmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    out = {}
    out['stdout'] = stdout.strip()
    out['stderr'] = stderr.strip()
    out['rc'] = process.returncode
    return out


def get_dump():
    bsock.sendall('dump\n')
    table_lines = bsock.recv(BABEL_BUFF).split('\n')
    while not is_end_string(table_lines[-2]):
        table_lines.extend(bsock.recv(BABEL_BUFF).split('\n'))
    return table_lines


def message_both(message):
    print message
    if GLOBAL_VARS["last_message"] != message:
        lcd.clear()
        lcd.message(message)
    GLOBAL_VARS["last_message"] = message


def intro():
    intro_message = ['Press up/dn\nto navigate',
                     'Welcome to\nAlthea Demo!',
                     'Set a price and\n watch peers',
                     'To best earn\na profit',
                     'Press Select\nFor main menu',
                     'Good luck!\nhave fun!']
    counter = 0
    changed = True
    while counter < len(intro_message):
        if changed:
            message_both(intro_message[counter])
            changed = False
        if lcd.is_pressed(LCD.UP) and counter > 0:
            counter = counter - 1
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            counter = counter + 1
            changed = True
        elif lcd.is_pressed(LCD.SELECT):
            break


def get_our_price():
    table_lines = get_dump()
    assert(is_end_string(table_lines[-2]))
    for table_line in table_lines:
        if 'local' in table_line and 'price' in table_line:
            if int(grab_babel_val(table_line, 'price')) is None:
                print(table_line)
            return int(grab_babel_val(table_line, 'price'))


def set_our_price(price):
    bsock.sendall('price {}\n'.format(price))
    print bsock.recv(BABEL_BUFF)

# Identifies babel message end strings


def is_end_string(message):
    # ok, no, bad are the only options
    if len(message) > 3:
        return False
    elif 'ok' in message or 'no' in message or 'bad' in message:
        return True
    else:
        return False

# Babel values are in the form of field value


def grab_babel_val(message, val):
    message = message.split(" ")
    for idx, item in enumerate(message):
        if val.lower() in item.lower():
            if message[idx + 1] is None:
                break
            return message[idx + 1]
    print("Looking for {} in {}".format(val, message))
    raise ValueError("Babel comm error")


def to_cash(num_bytes, price):
    return (float(num_bytes) / 1000000000) * price


def get_total_forwarded():
    return int(run_cmd("iptables -L -n -v -x | awk '/FORWARD/ { print $7; }'")['stdout'])


def view_earnings():
    last_update = datetime.datetime.utcnow()
    current_price = get_our_price()
    price_step = 10
    while True:
        if lcd.is_pressed(LCD.SELECT):
            return
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
                total_bytes = get_total_forwarded()
                current_bytes = total_bytes - GLOBAL_VARS["last_total_bytes"]
                if current_bytes > 0:
                    current_earnings = to_cash(current_bytes, get_our_price())
                    current_kbs = current_bytes / 1000
                    message = "{:.0f}kbs +${:.2f}\nTotal: ${:.2f}"
                    message_both(message.format(
                        current_kbs, current_earnings, GLOBAL_VARS["total_earnings"]))
                    last_update = datetime.datetime.utcnow()
                    total_earnings = GLOBAL_VARS["total_earnings"] + \
                        current_earnings
                else:
                    message = "0kbs\nTotal: ${:.2f}"
                    message_both(message.format(total_earnings))

                last_total_bytes = total_bytes


lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()

proc = Proc()
bsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to\nBabel...')
bsock.connect((BABEL_IP, BABEL_PORT))
print bsock.recv(BABEL_BUFF)
message_both('Connected to\nBabel!')

if GROUP == "gateway":
    message_both('gateway')

if GROUP == "client":
    message_both('client')

if GROUP == "intermediary":
    message_both('intermediary')
    view_earnings()
