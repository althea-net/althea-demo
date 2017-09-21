#!/usr/bin/python
"""Runs user interface for intermediary nodes"""

import time
import datetime
import socket
from common import message_both, run_cmd, json_post_cmd, run_cmd_nowait
import Adafruit_CharLCD as lcd

# {% if 'intermediary' in group_names %}

NAME = "{{name}}"
MESH_IP = "{{mesh_ip}}"

# {% endif %}

HOSTNAME = "{{inventory_hostname}}"
STAT_SERVER = "http://{{gateway_mesh_ip}}:{{stat_server_port}}"

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072

GATEWAY_IP = "{{gateway_mesh_ip}}"

GLOBAL_VARS = {
    "last_message": "",
    "last_total_bytes": 0,
    "total_earnings": 0
}


def get_dump():
    """Get babel's dump"""
    BABEL_SOCKET.sendall('dump\n')
    table_lines = BABEL_SOCKET.recv(BABEL_BUFF).split('\n')
    while not is_end_string(table_lines[-2]):
        table_lines.extend(BABEL_SOCKET.recv(BABEL_BUFF).split('\n'))
    return table_lines


def get_our_price():
    """Get our current price from babel"""
    table_lines = get_dump()
    assert is_end_string(table_lines[-2])
    for table_line in table_lines:
        if 'local' in table_line and 'price' in table_line:
            if int(grab_babel_val(table_line, 'price')) is None:
                print table_line
            return int(grab_babel_val(table_line, 'price'))


def set_our_price(price):
    """Set our current price on babel"""
    BABEL_SOCKET.sendall('price {}\n'.format(price))
    print BABEL_SOCKET.recv(BABEL_BUFF)


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
    print "Looking for {} in {}".format(val, message)
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


def update_earnings_info(message, current_price):
    """send and display earnings update"""
    message_both(message, LCD)
    cmd = json_post_cmd({"id": NAME, "message": message, "price": current_price,
                         "total": GLOBAL_VARS["total_earnings"]}, STAT_SERVER)
    run_cmd_nowait(cmd)
    return datetime.datetime.utcnow(), message


def active_earnings_message(current_bytes, current_earnings):
    """generate earnings message when actively earning"""
    current_kbs = current_bytes / 1000
    return "{:.0f} kb +${:<8.2f}\nTotal: ${:8.2f}".format(
        current_kbs, current_earnings, GLOBAL_VARS["total_earnings"])


def inactive_earnings_message():
    """generate earnings message when not earning"""
    return "0 kb\nTotal: ${:.2f}".format(
        GLOBAL_VARS["total_earnings"])


def price_up(current_price, price_step):
    current_price = max(current_price + int(1 * (price_step / 10)), 0)
    set_our_price(current_price)
    price_step = max(price_step * 1.3, 500)
    message_both("Cents per GB:\n{}".format(current_price), LCD)

    for i in range(10):
        if LCD.is_pressed(lcd.UP):
            return price_up(current_price, price_step)
        if LCD.is_pressed(lcd.DOWN):
            return price_down(current_price, price_step)
        time.sleep(0.1)

    current_price = get_our_price()
    return current_price, price_step


def price_down(current_price, price_step):
    current_price = max(current_price - int(1 * (price_step / 10)), 0)
    set_our_price(current_price)
    price_step = max(price_step * 1.3, 500)
    message_both("Cents per GB:\n{}".format(current_price), LCD)

    for i in range(10):
        if LCD.is_pressed(lcd.UP):
            return price_up(current_price, price_step)
        if LCD.is_pressed(lcd.DOWN):
            return price_down(current_price, price_step)
        time.sleep(0.1)

    current_price = get_our_price()
    current_price = get_our_price()
    return current_price, price_step


def view_earnings():
    """Main screen"""
    last_update = datetime.datetime.utcnow()
    current_price = get_our_price()
    price_step = 10
    while True:
        if LCD.is_pressed(lcd.UP):
            (current_price, price_step) = price_up(current_price, price_step)
        elif LCD.is_pressed(lcd.DOWN):
            (current_price, price_step) = price_down(current_price, price_step)
        elif LCD.is_pressed(lcd.LEFT):
            message_both("{}\n{}".format(MESH_IP, HOSTNAME), LCD)
            time.sleep(2)
        elif LCD.is_pressed(lcd.RIGHT):
            message_both("Name:\n{}".format(NAME), LCD)
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


LCD = lcd.Adafruit_CharLCDPlate()

BABEL_SOCKET = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to\nBabel...', LCD)
BABEL_SOCKET.connect((BABEL_IP, BABEL_PORT))
print BABEL_SOCKET.recv(BABEL_BUFF)
message_both('Connected to\nBabel!', LCD)

message_both('intermediary', LCD)
view_earnings()
