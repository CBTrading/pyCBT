#!/usr/bin/env python
#
# This script writes the configuration file for using the OANDA API

import argparse, os, urllib2, json, string
from copy import copy
from collections import OrderedDict
from pyCBT.data.providers.oanda import account
import oandapyV20
from oandapyV20.endpoints.accounts import AccountList

# THE FOLLOWING BLOCK OF CODE WAS COPIED FROM
# https://github.com/oanda/v20-python-samples/blob/master/src/market_order_full_example.py
# --------------------------------------------------------------------------------------------------
#
# Add arguments for API connection
#
account_attrs = copy(account.ATTRS)

account_attrs.pop("accounts")
account_attrs.pop("active_account")

parser = argparse.ArgumentParser()

for arg in account_attrs.keys():
    kwargs = copy(account_attrs[arg])
    if kwargs.has_key("choices"): kwargs.pop("choices")
    parser.add_argument("--{}".format(arg), **kwargs)

args = parser.parse_args()

config = account.Config(**dict(args._get_kwargs()))
account_info = config.info
config.set_to_file(config.filename)

print account_info
