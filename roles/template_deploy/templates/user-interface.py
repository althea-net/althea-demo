#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import Adafruit_CharLCD as LCD
import numpy
from numpy import mean
import datetime
import os
import subprocess
import socket
import sys
from procfs import Proc

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072
# Used in place of tunnel negotiation
GATEWAY_IP = "10.28.7.7"


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
    lcd.clear()
    lcd.message(message)
    print(message)


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
    time.sleep(1)
    table_lines = get_dump()
    assert(is_end_string(table_lines[-2]))
    for table_line in table_lines:
        if 'local' in table_line and 'price' in table_line:
            if int(grab_babel_val(table_line, 'price')) is None:
                print(table_line)
            return int(grab_babel_val(table_line, 'price'))


def get_gateway_price():
    time.sleep(1)
    table_lines = get_dump()
    assert(is_end_string(table_lines[-2]))
    for table_line in table_lines:
        if GATEWAY_IP in table_line and 'price' in table_line and 'installed' in table_line:
            if int(grab_babel_val(table_line, 'price')) is None:
                print(table_line)
            return int(grab_babel_val(table_line, 'price'))
        elif GATEWAY_IP in table_line and 'xroute' in table_line:
            return get_our_price()
    # No installed route to the gateway
    return 0


def set_our_price(price):
    bsock.sendall('price {}\n'.format(price))
    print bsock.recv(BABEL_BUFF)

def adjust_price():
    current_price = get_our_price()
    changed = True
    held = 10
    msg_str = "Price in cents\nTB:{} up/dn"
    while not lcd.is_pressed(LCD.SELECT):
        if changed:
            message_both(msg_str.format(current_price))
            changed = False
        if lcd.is_pressed(LCD.UP):
            current_price = max(current_price + int(1 * (held / 10)), 0)
            set_our_price(current_price)
            changed = True
            held = held * 1.5
        elif lcd.is_pressed(LCD.DOWN):
            current_price = max(current_price - int(1 * (held / 10)), 0)
            set_our_price(current_price)
            changed = True
            held = held * 1.5
        else:
            held = max(held/2, 10)

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


def get_neigh_stats():
    table_lines = get_dump()
    num_neighs = 0
    reach_vals = []
    metric_arr = []
    for table_line in table_lines:
        print table_line
        if 'neighbour' in table_line:
            num_neighs = num_neighs + 1
            neigh_id = grab_babel_val(table_line, 'neighbour')
            neigh_metric = int(grab_babel_val(table_line, 'cost'))
            reach_val = "ID: {}\nQ: {} ".format(neigh_id, neigh_metric)
            metric_arr.append(neigh_metric)
            reach_vals.append(reach_val)
    if len(metric_arr) == 0:
        metric_avg = 0
    else:
        metric_arr = numpy.array(metric_arr)
        metric_avg = int(metric_arr.mean())
    return num_neighs, reach_vals, metric_avg


def view_neighs():
    num_neighs, reach_vals, avg_cost = get_neigh_stats()
    message_string = "{} Neighbors \nAvg Q: {}"
    neigh_message = [message_string.format(num_neighs,
                                           avg_cost)]
    neigh_message.extend(reach_vals)

    counter = 0
    changed = True
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        now = datetime.datetime.utcnow()
        if changed:
            message_both(neigh_message[counter])
            changed = False
        if lcd.is_pressed(LCD.UP):
            if counter > 0:
                counter = counter - 1
            else:
                counter = 0
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            counter = (counter + 1) % len(neigh_message)
            changed = True
        elif now - last_update > datetime.timedelta(seconds=5):
            num_neighs, reach_vals, avg_cost = get_neigh_stats()
            neigh_message = [message_string.format(num_neighs,
                                                   avg_cost)]
            neigh_message.extend(reach_vals)
            last_update = datetime.datetime.utcnow()
            if counter >= len(neigh_message):
                counter = len(neigh_message) - 1
            changed = True


def get_route_stats():
    our_price = get_our_price()
    table_lines = get_dump()
    # If this is false someone left the connection in a strange state
    assert(is_end_string(table_lines[-2]))
    num_routes = 0
    reach_vals = []
    price_arr = []
    metric_arr = []
    for table_line in table_lines:
        print table_line
        if 'route' in table_line and 'xroute' not in table_line and 'installed yes' in table_line:
            num_routes = num_routes + 1
            route_id = grab_babel_val(table_line, 'route')
            refmetric = int(grab_babel_val(table_line, 'refmetric'))
            if refmetric == 0:
                hops = '1'
            else:
                hops = '>'
            # Quirk of the way prices are advertised
            route_price = int(grab_babel_val(table_line, 'price')) - our_price
            route_qual = int(grab_babel_val(table_line, 'metric'))
            reach_val = "Route: {}\nQ {} P {} H {}".format(
                route_id, route_qual, route_price, hops)
            metric_arr.append(route_qual)
            price_arr.append(route_price)
            reach_vals.append(reach_val)
    if len(metric_arr) == 0:
        metric_avg = 0
    else:
        metric_arr = numpy.array(metric_arr)
        metric_avg = int(metric_arr.mean())
    if len(price_arr) == 0:
        price_avg = 0
    else:
        price_arr = numpy.array(price_arr)
        price_avg = int(price_arr.mean())
    return num_routes, reach_vals, price_avg, metric_avg


def view_routes():
    num_routes, reach_vals, avg_price, avg_metric = get_route_stats()
    message_string = "{} routes  Avg\nP: {} Q: {}"
    route_message = [message_string.format(num_routes,
                                           avg_price,
                                           avg_metric)]
    route_message.extend(reach_vals)
    counter = 0
    changed = True
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        if changed:
            message_both(route_message[counter])
            changed = False
        if lcd.is_pressed(LCD.UP):
            if counter > 0:
                counter = counter - 1
            else:
                counter = 0
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            counter = (counter + 1) % len(route_message)
            changed = True
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=5):
            num_routes, reach_vals, avg_price, avg_metric = get_route_stats()
            route_message = [message_string.format(num_routes,
                                                   avg_price,
                                                   avg_metric)]
            route_message.extend(reach_vals)
            if counter >= len(route_message):
                counter = len(route_message) - 1
            last_update = datetime.datetime.utcnow()
            changed = True


def to_cash(num_bytes, price):
    return (float(num_bytes) / 10000000) * price

def get_total_forwarded():
    return int(run_cmd("iptables -L -n -v -x | awk '/FORWARD/ { print $7; }'")['stdout'])

# def update_earnings(last_bytes, total_earnings):
#     total_bytes = get_total_forwarded()
#     current_earnings = to_cash(total_bytes - last_bytes, get_our_price())
#     total_earnings = total_earnings + current_earnings
#     last_bytes = total_bytes
#     return (last_bytes, total_earnings, current_earnings)

def earnings_message(current_bytes, current_earnings, total_earnings):
    current_kbs = current_bytes / 1000
    if current_earnings > 0:
        message = "{0}kbs +{1}¢\nTotal: ${2}"
        return message.format(current_kbs, current_earnings, total_earnings)
    else:
        message = "{0}kbs\nTotal: ${1}"
        return message.format(current_kbs, total_earnings)

def view_earnings(last_total_bytes, total_earnings):
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=1):
            last_update = now

            total_bytes = get_total_forwarded()
            current_bytes = total_bytes - last_total_bytes
            current_earnings = to_cash(current_bytes, get_our_price())
            total_earnings = total_earnings + current_earnings

            message_both(earnings_message(current_bytes, current_earnings, total_earnings))

            last_total_bytes = total_bytes

    return total_bytes, total_earnings


def main_menu():
    menu_message = ['Main Menu\nPress Up/Dn',
                    'View neighbors >',  # 1
                    'View routes >',  # 2
                    'View earnings >',  # 3
                    'Adjust Price >',  # 4
                    'Shutdown >']  # 5
    counter = 0
    changed = True
    last_bytes = 0
    total_earnings = 0
    last_bytes, total_earnings = view_earnings(last_bytes, total_earnings)
    while True:
        if changed:
            message_both(menu_message[counter])
            changed = False
        if lcd.is_pressed(LCD.UP):
            if counter > 0:
                counter = counter - 1
            else:
                counter = len(menu_message) - 1
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            counter = (counter + 1) % len(menu_message)
            changed = True
        elif lcd.is_pressed(LCD.RIGHT):
            if counter == 1:
                message_both("Loading...")
                view_neighs()
            elif counter == 2:
                message_both("Loading...")
                view_routes()
            elif counter == 3:
                message_both("Loading...")
                last_bytes, total_earnings = view_earnings(
                    last_bytes, total_earnings)
            elif counter == 4:
                # If we don't update earnings before entering this function we
                # can miscount
                message_both("Loading...")
                # last_bytes, total_earnings = update_earnings(
                    # last_bytes, total_earnings)
                adjust_price()
            elif counter == 5:
                message_both("Goodbye!")
                run_cmd("sudo shutdown now")
            changed = True
        time.sleep(.05)

lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()

proc = Proc()
bsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to\nBabel...')
bsock.connect((BABEL_IP, BABEL_PORT))
print bsock.recv(BABEL_BUFF)
message_both('Connected to\nBabel!')

{% if 'gateway' in group_names %}
message_both('gateway')
{% elif  'client' in group_names %}
message_both('client')
{% else %}
message_both('intermediary')
main_menu()
{% endif %}