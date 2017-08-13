#!/usr/bin/python
import time
import Adafruit_CharLCD as LCD
from numpy import mean
import datetime
import os
import argparse
import socket
from procfs import Proc

BABEL_IP = "::1"
BABEL_PORT = "8080"
BABEL_BUFF = "4096"
INTERFACE_NAME = 'wlan0'


lcd = LCD.Adafruit_CharLCDPlate()
lcd.clear()
first_entry = True

bsock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
message_both('Connecting to Babel')
s.connect((BABEL_IP, BABEL_PORT))
if 'ok' not in s.recv(BABEL_BUFF):
    message_both('Bad Babel conn')
    exit(1)
message_both('Connected to Babel')

proc = PROC()

def message_both(message):
    lcd.message(message)
    print(message)

def intro():
    intro_message = ['Press up/down to navigate',
                     'Press Select to go to main menu',
                     'Althea Demo!',
                     'More instructions here later',
                     'You can press select on the main menu to see this again',
                     'Good luck have fun!']
    counter = 0
    while counter > intro_message.len():
        message_both(intro_message[counter])
        if lcd.is_pressed(LCD.UP) and counter > 0:
            counter = counter - 1
        elif lcd.is_pressed(LCD.DOWN):
            counter = counter + 1
        elif lcd.is_pressed(LCD.SELECT):
            break

def adjust_price():
    pass

# Identifies babel message end strings
def is_end_string(mesage):
    #ok, no, bad are the only options
    if message.len() > 3:
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
            return message[idx + 1]
    raise ValueError:
        message_both("Babel comm error")

def get_neigh_stats():
    bsock.sendall('dump\n')
    table_line = bsock.recv(BABEL_BUFF)
    num_neighs = 0
    reach_vals = []
    cost_arr = []
    while not is_end_string(table_line):
        if 'neighbor' in table_line:
            num_neighs = num_neighs + 1
            neigh_id = grab_babel_val(table_line, 'neighbour')
            neigh_cost = grab_babel_val(table_line, 'cost')
            reach_val = " {}: {} ,".format(neigh_id, neigh_cost)
            cost_arr.append(neigh_cost)
            message_both()
        table_line = bsock.recv(BABEL_BUFF)
    return num_neighs, reach_vals, cost_arr.mean()


def view_neighs():
    num_neighs, reach_vals, avg_cost = get_neigh_stats()
    neigh_message = ["You have {} Neighbors \n Avg qual is {}".format(num_neighs,
                                                                      avg_cost),
                     ].extend(reach_vals)
    counter = 0
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        message_both(neigh_message[counter])
        if lcd.is_pressed(LCD.UP):
            counter = (counter + 1) % neigh_message.len() - 1
        elif lcd.is_pressed(LCD.DOWN):
            if counter > 0:
                counter = counter - 1
            else:
                counter = neigh_message.len() - 1
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=5):
            num_neighs, reach_vals, avg_cost = get_neigh_stats()
            neigh_message = ["You have {} Neighbors \n Avg qual is {}".format(num_neighs,
                                                                              avg_cost),
                            ].extend(reach_vals)
            last_update = datetime.datetime.utcnow()
            if counter >= neigh_message.len():
                counter = neigh_message.len() - 1
    main_menu()

def get_route_stats():
    bsock.sendall('dump\n')
    table_line = bsock.recv(BABEL_BUFF)
    num_routes = 0
    reach_vals = []
    price_arr = []
    metric_arr = []
    while not is_end_string(table_line):
        if 'route' in table_line:
            num_routes = num_routes + 1
            route_id = grab_babel_val(table_line, 'route')
            route_price = grab_babel_val(table_line, 'Price')
            route_qual = grab_babel_val(table_line, 'metric')
            reach_val = " {}: Metric {} Price {},".format(route_qual, route_price)
            metric_arr.append(route_qual)
            price_arr.append(route_price)
            message_both()
        table_line = bsock.recv(BABEL_BUFF)
    return num_routes, reach_vals, price_arr.mean(), metric_arr.mean()

def view_routes():
    num_routes, reach_vals, avg_price, avg_metric = get_route_stats()
    route_message = ["You have {} routes \n Avg Price: {}, Avg Qual: {}".format(num_routes,
                                                                                avg_price,
                                                                                avg_metric)
                     ].extend(reach_vals)
    counter = 0
    last_update = datetime.datetime.utcnow()
    while not lcd.is_pressed(LCD.SELECT):
        message_both(route_message[counter])
        if lcd.is_pressed(LCD.UP):
            counter = (counter + 1) % route_message.len() - 1
        elif lcd.is_pressed(LCD.DOWN):
            if counter > 0:
                counter = counter - 1
            else:
                counter = route_message.len() - 1
        now = datetime.datetime.utcnow()
        if now - last_update > datetime.timedelta(seconds=5):
            num_routes, reach_vals, avg_price, avg_metric = get_route_stats()
            route_message = ["You have {} routes \n Avg Price: {}, Avg Qual: {}".format(num_routes,
                                                                                        avg_price,
                                                                                        avg_metric)
                     ].extend(reach_vals)
            if counter >= route_message.len():
                counter = route_message.len() - 1
            last_update = datetime.datetime.utcnow()
    main_menu()

def view_earnings():
    while not lcd.is_pressed(LCD.SELECT):
        # Need to think of a better way to do this
        forwarded_traffic = min(proc.net.dev.INTERFACE_NAME.recv.bytes,
                                proc.net.dev.INTERFACE_NAME.send.bytes)
        message_both(forwarded_traffic)
    main_menu()


def main_menu():
    if first_entry:
        intro()
        first_entry = False

    menu_message = ['Main Menu \n Press > to select',
                    'View neighbors >', # 1
                    'View routes >', # 2
                    'View earnings >', # 3
                    'Adjust Price >'] # 4
    counter = 0
    while True:
        message_both(menu_message[counter])
        if lcd.is_pressed(LCD.UP):
            counter = (counter + 1) % menu_message.len() - 1
        elif lcd.is_pressed(LCD.DOWN):
            if counter > 0:
                counter = counter - 1
            else:
                counter = menu_message.len() - 1
        elif lcd.is_pressed(LCD.RIGHT):
            if counter == 1:
                view_neighs()
            elif counter == 2:
                view_routes()
            elif counter == 3:
                view_earnings()
            elif counter == 4:
                adjust_price()
        elif lcd.is_pressed(LCD.SELECT):
            intro():


main_menu()
