#!/usr/bin/env python

import socket
import time
import json
from threading import Thread
from . import args

ip = args["roborio_ip"]
port = int(args["roborio_port"])
verbose = args["verbose"]

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send(message, recipient=(ip, port)):
    message['time'] = int(time.time() * 1000)
    sock.sendto(json.dumps(message, separators=(',', ':')).encode(), recipient)
