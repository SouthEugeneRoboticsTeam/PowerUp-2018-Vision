#!/usr/bin/env python

import logging
import subprocess
from networktables import NetworkTables
from . import args, NetworkTablesException

ip = args["roborio_ip"]
verbose = args["verbose"]

vision_table = False
v4l2_table = False

def v4l2_changed(table, key, value, new):
    subprocess.call("v4l2-ctl -c {}={}".format(key, value), shell=True)

if verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if ip is not None:
    NetworkTables.initialize(server=ip)

    vision_table = NetworkTables.getTable("Vision")
    v4l2_table = NetworkTables.getTable("v4l2")

    v4l2_table.addEntryListener(v4l2_changed)


def put_number(key, value):
    if vision_table:
        return vision_table.putNumber(key, value)
    elif verbose:
        print("[NetworkTables] not connected")
    raise NetworkTablesException("Not connected to NetworkTables")


def put_boolean(key, value):
    if vision_table:
        return vision_table.putBoolean(key, value)
    elif verbose:
        print("[NetworkTables] not connected")
    raise NetworkTablesException("Not connected to NetworkTables")


def get_boolean(key, default):
    if vision_table:
        return vision_table.getBoolean(key, default)
    elif verbose:
        print("[NetworkTables] not connected")
    return default


def get_number(key, default):
    if vision_table:
        return vision_table.getNumber(key, default)
    elif verbose:
        print("[NetworkTables] not connected")
    return default
