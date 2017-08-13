#!/usr/bin/python
import time
import Adafruit_CharLCD as LCD
import numpy
from numpy import mean
import datetime
import os
import socket
from procfs import Proc

BABEL_IP = "::1"
BABEL_PORT = 8080
BABEL_BUFF = 131072


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

def set_our_price(price):
    bsock.sendall('price {}\n'.format(price))
    print bsock.recv(BABEL_BUFF)



def adjust_price():
    current_price = get_our_price()
    changed = True
    msg_str = "Price in cents\nGig:{} up/dn"
    while not lcd.is_pressed(LCD.SELECT):
        if changed:
            message_both(msg_str.format(current_price))
            changed = False
        elif lcd.is_pressed(LCD.UP):
            current_price = current_price + 1
            set_our_price(current_price)
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            current_price = current_price - 1
            set_our_price(current_price)
            changed = True

# Identifies babel message end strings
def is_end_string(message):
    #ok, no, bad are the only options
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
        if val in item:
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
        if 'route' in table_line and 'xroute' not in table_line:
            num_routes = num_routes + 1
            route_id = grab_babel_val(table_line, 'route')
            # Quirk of the way prices are advertised
            route_price = int(grab_babel_val(table_line, 'Price')) - our_price
            route_qual = int(grab_babel_val(table_line, 'metric'))
            reach_val = "Route: {}\nQ {} P {}".format(route_id, route_qual, route_price)
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

def update_earnings(last_bytes, total_earings):
    price_per_byte = get_our_price()
    forwarded_traffic = min(proc.net.dev.wlan0.transmit.bytes,
                        proc.net.dev.wlan0.receive.bytes) - last_bytes
    last_bytes = min(proc.net.dev.wlan0.transmit.bytes,
                     proc.net.dev.wlan0.receive.bytes)
    # never use this in real life, floats for money are BAD
    total_earings = total_earings + (float(forwarded_traffic) / 1073741824) * price_per_byte
    return last_bytes, total_earings

# This is broken and simple to cheat, fix later
def view_earnings(last_bytes, total_earings):
    changed = True
    message = "Total Earned\n${0:.15f}"
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        now = datetime.datetime.utcnow()
        if changed:
            message_both(message.format(total_earings))
            changed = False
        elif now - last_update > datetime.timedelta(seconds=1):
            changed = True
            last_update = now
            last_bytes, total_earings = update_earnings(last_bytes, total_earings)
    return last_bytes, total_earings


def main_menu():
    menu_message = ['Main Menu\nPress Up/Dn',
                    'View neighbors >', # 1
                    'View routes >', # 2
                    'View earnings >', # 3
                    'Adjust Price >'] # 4
    counter = 0
    changed = True
    last_bytes = min(proc.net.dev.wlan0.transmit.bytes,
                    proc.net.dev.wlan0.receive.bytes)
    total_earings = 0
    while True:
        if changed:
            message_both(menu_message[counter])
            changed = False
        if lcd.is_pressed(LCD.UP):
            counter = (counter + 1) % len(menu_message)
            changed = True
        elif lcd.is_pressed(LCD.DOWN):
            if counter > 0:
                counter = counter - 1
            else:
                counter = len(menu_message) - 1
            changed = True
        elif lcd.is_pressed(LCD.RIGHT):
            if counter == 1:
                view_neighs()
            elif counter == 2:
                view_routes()
            elif counter == 3:
                last_bytes, total_earings = view_earnings(last_bytes, total_earings)
            elif counter == 4:
                # If we don't update earnings before entering this function we can miscount
                last_bytes, total_earings = update_earnings(last_bytes, total_earings)
                adjust_price()
            changed = True

lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()

proc = Proc()
bsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to\nBabel...')
bsock.connect((BABEL_IP, BABEL_PORT))
print bsock.recv(BABEL_BUFF)
message_both('Connected to\nBabel!')


intro()
main_menu()
