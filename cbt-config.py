#!/usr/bin/env python
#
# This script writes the configuration file for using the OANDA API

import argparse, os, sys
from copy import copy
from collections import OrderedDict
from pyCBT.data.providers.oanda import account

# define parser
parser = argparse.ArgumentParser()
# define config
config = account.Config()
# add parameters to parser
for arg in config.attr_names:
    # don't include accounts in parser
    if arg == "accounts": continue
    # define attribute keywords for safe manipulation
    kwargs = OrderedDict()
    kwargs["help"] = config.attr_helps[arg]
    if config.attr_types[arg] is not None:
        kwargs["type"] = config.attr_types[arg]
    # add attribute to parser
    parser.add_argument("--{}".format(arg), **kwargs)
# add interactive option
parser.add_argument("--interactive", help="Update config attributes interatively", action="store_true")
# parse arguments from command line (cmd)
args = parser.parse_args()
# build cmd arguments for configuration file
cmd_kwargs = dict(args._get_kwargs())
cmd_kwargs.pop("interactive")
# clean None values from cmd_kwargs
cmd_kwargs = dict((arg, val) for arg, val in cmd_kwargs.iteritems() if val is not None)
# check if 'active_account' is in command line arguments
fil_kwargs = OrderedDict()
if cmd_kwargs.has_key("active_account"):
    # define filename
    filename = config.get_filename(cmd_kwargs.get("active_account"))
    # check if config file already exist
    if os.path.isfile(filename):
        response = "y"
        if args.interactive:
            print
            response = raw_input("Going to load config file '{}' [Y/n]: ".format(os.path.basename(filename)))
        if not response or response.lower().startswith("y"):
            with open(filename, "r") as IN:
                fil_kwargs.update(config.get_from(IN))
# update attribute defaults to file if available & command line argument values, in that order
config.update_defaults(**fil_kwargs)
config.update_defaults(**cmd_kwargs)
# ask/set account attributes
# ask if interactive or fil_kwargs is empty
if args.interactive or not fil_kwargs:
    config.ask_account()
    config.ask_attributes()
else:
    config.set_account()
    config.set_attributes()
# set summary config
config.set_summary()
# display summary
print
print "Summary config:"
print
config.dump_to(sys.stdout)
# define filename
filename = config.get_filename()
# save to file?
# default response
response = "Y"
print
response = raw_input("Save summary to '{}' [Y/n]: ".format(os.path.basename(filename)))
if response.lower().startswith("y") or response == "":
    with open(filename, "w") as OUT:
        config.dump_to(OUT)
    if args.interactive:
        print "Config file saved."
print
