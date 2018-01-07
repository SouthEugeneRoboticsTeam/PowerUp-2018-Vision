#!/usr/bin/env python

from . import utils

args = utils.get_args()


class NetworkTablesException(Exception):
    pass
