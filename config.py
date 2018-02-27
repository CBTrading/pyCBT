#!/usr/bin/env python
#
# This script writes the configuration file for using the OANDA API

import argparse, os
from copy import copy
from pyCBT.data.providers.oanda import account

account_attrs = copy(account.ATTRS)
account_attrs["active_account"] = dict(
    help="Active account"
)

parser = argparse.ArgumentParser()

for arg in account_attrs.keys():
    # define attribute keywords for safe manipulation
    kwargs = copy(account_attrs[arg])
    # remove choices
    if kwargs.has_key("choices"): kwargs.pop("choices")
    # remove default values
    if kwargs.has_key("default"): kwargs.pop("default")
    # add attribute to parser
    parser.add_argument("--{}".format(arg), **kwargs)

# parse arguments from command line (cmd)
args = parser.parse_args()
# build cmd arguments for configuration file
cmd_kwargs = dict(args._get_kwargs())
kw_toremove = []
for attr in cmd_kwargs:
    # remove None values
    if cmd_kwargs[attr] is None:
        kw_toremove.append(attr)
for attr in kw_toremove: cmd_kwargs.pop(attr)

# create config object
config = account.Config(interactive=True, **cmd_kwargs)
# build account summary
account_info = config.info
# dump summary to default file
config.set_to_file(config.filename)
