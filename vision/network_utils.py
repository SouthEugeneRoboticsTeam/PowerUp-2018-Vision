#!/usr/bin/env python

import socket
import time
import json
from . import args

ip = args["roborio_ip"]
port = int(args["roborio_port"])
verbose = args["verbose"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send(message, recipient=(ip, port)):
    print(message)
    message['time'] = int(time.time() * 1000)
    sock.sendto(json.dumps(message, separators=(',', ':')).encode(), recipient)


def send_heartbeat():
    send({"alive": True})


def send_heartbeat_end():
    send({"alive": False})


def send_found(offset_x, offset_y):
    send({
        "found": True,
        "offset_x": offset_x,
        "offset_y": offset_y
    })


def send_not_found():
    send({
        "found": False
    })
