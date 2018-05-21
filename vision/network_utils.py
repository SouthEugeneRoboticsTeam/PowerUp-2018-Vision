#!/usr/bin/env python

import socket
import time
import json
from . import args

global prev_message
global prev_recipient
global prev_time

ip = args["roborio_ip"]
port = int(args["roborio_port"])
verbose = args["verbose"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

prev_message = {}
prev_recipient = ()
prev_time = 0


def send(message, recipient=(ip, port)):
    """
    Sends a packet to the specified recipient. For broadcasts, IP should be
    10.25.21.255, with a port in range of 5800-5810. In most cases, the recipient
    should be the roboRIO.

    :param message: the dict to send as a message (will be converted to JSON and a
                    timestamp will be added)
    :param recipient: the recipient of the packet
    """
    message["time"] = int(time.time() * 1000)
    sock.sendto(json.dumps(message, separators=(",", ":")).encode(), recipient)


def send_new(message, recipient=(ip, port)):
    """
    Sends a packet to the specified recipient if either the message or the recipient
    has changed from the last call of this method, or if 500ms have passed since the
    last time a message has been sent.

    :param message: the dict to send as a message (will be converted to JSON and a
                    timestamp will be added)
    :param recipient: the recipient of the packet
    """
    global prev_message
    global prev_recipient
    global prev_time

    timeout = int(time.time() * 1000) - prev_time > 500
    if message != prev_message or recipient != prev_recipient or timeout:
        prev_message = dict(message)
        prev_recipient = tuple(recipient)
        prev_time = int(time.time() * 1000)

        send(message, recipient)
