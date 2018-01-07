#!/usr/bin/env python

import logging
from networktables import NetworkTables
from . import args, NetworkTablesException

ip = args["roborio_ip"]
verbose = args["verbose"]

vision_table = False

if verbose:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

if ip is not None:
    NetworkTables.initialize(server=ip)

    vision_table = NetworkTables.getTable("Vision")


def put_number(key, value):
    if vision_table:
        vision_table.putNumber(key, value)
    elif verbose:
        print("[NetworkTables] not connected")
    raise NetworkTablesException("Not connected to NetworkTables")


def put_boolean(key, value):
    if vision_table:
        vision_table.putBoolean(key, value)
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
