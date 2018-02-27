#!/usr/bin/env python
#
# This script writes the configuration file for using the OANDA API

import argparse, os, urllib2, json
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

account_attrs = OrderedDict(
    hostname=dict(default="api-fxpractice.oanda.com", help="Server hostname"),
    streaming_hostname=dict(default="stream-fxpractice.oanda.com", help="Streaming Server hostname"),
    port=dict(type=int, default=443, help="Server port"),
    ssl=dict(type=bool, default=True, help="Allow SSL protocol"),
    token=dict(help="API Auth Token"),
    username=dict(help="Username of the account owner"),
    datetime_format=dict(help="Datetime format"),
    accounts=dict(help="List of accounts owned by user"),
    active_account=dict(help="Active account")
)

parser = argparse.ArgumentParser()

for arg in account_attrs:
    if arg in ["accounts", "active_account"]: continue
    parser.add_argument("--{}".format(arg), **account_attrs[arg])

args = parser.parse_args()
account_config = account.Config(**dict(args._get_kwargs()))
account_info = account_config.info

api = oandapyV20.API(access_token=account_info["token"])
for arg in account_info:
    if account_info["token"] and arg == "accounts":
        r = AccountList()
        api.request(r)
        account_info["accounts"] = [account["id"] for account in r.response["accounts"]]
    if account_info["accounts"] and arg == "active_account":
        print "Available accounts:"
        for l, a in zip(strings.lowercase, account_info["accounts"]): print "<{}> {}".format(l, a)
        print "{}".format(account_attrs[arg]["help"])
    while account_info[arg] is None:
        account_info[arg] = raw_input("{} [{}]: ".format(account_attrs[arg].get("help"), account_attrs[arg].get("default")))
        if account_info[arg] == "": account_info[arg] = arg_attrs.get("default")


# try:
#     account_info = account.Config(**account_info._get_kwargs())
# except ValueError as err:
#     missing_arg, = err.args
#
#     if missing_arg in ["accounts", "active_account"] and account_info["token"]:
#         pass
#
#     account_info[missing_arg] = None
#     while account_info[missing_arg] is None:
#         account_info[missing_arg] = raw_input("Please enter {} [{}]: ".format(missing_arg, parser.get_default(missing_arg)))
#         if account_info[missing_arg] == "":
#             account_info[missing_arg] = parser.get_default(missing_arg)
#         if account_info[missing_arg] == "?":
#             print parser
#             account_info[missing_arg] = None
#             print
#         else:
#             print

# account_info = dict(args._get_kwargs())
# missing_args = {"username": "Your username in OANDA",
#                 "token": "v20 Auth Token"}
#
# print
# for arg in missing_args:
#     while account_info[arg] is None:
#         account_info[arg] = raw_input("Please enter {}: ".format(arg))
#         if account_info[arg] == "?":
#             print missing_args[arg]
#             account_info[arg] = None
#             print
#         else:
#             print
#
# request = urllib2.Request(
#     "{}{}".format("https://api-fxpractice.oanda.com", "/v3/accounts"),
#     headers={"Content-Type": "application/json",
#              "Authorization": "Bearer {}".format(args.token)}
# )
#
# account_info["accounts"] = json.load((urllib2.urlopen(request)))["accounts"]
# account_info["active_account"] = account_info["accounts"][0]["id"]

# END OF COPIED CODE -------------------------------------------------------------------------------
# WRITE CONFIG FILE IN HOME DIRECTORY
# with open("{}/.pycbt-config.yml".format(os.environ["HOME"]), "w") as conf_file:
#
#     conf_file.write("hostname: {}{}".format(account_info["hostname"], os.linesep))
#     conf_file.write("streaming_hostname: {}{}".format(account_info["streaming_hostname"], os.linesep))
#     conf_file.write("port: {}{}".format(account_info["port"], os.linesep))
#     conf_file.write("token: {}{}".format(account_info["token"], os.linesep))
#     conf_file.write("username: {}{}".format(account_info["username"], os.linesep))
#     conf_file.write("accounts:{}".format(os.linesep))
#     for account in account_info["accounts"]:
#         conf_file.write("- {}{}".format(account["id"], os.linesep))
#     conf_file.write("active_account: {}{}".format(account_info["active_account"], os.linesep))
#     conf_file.write(os.linesep)
