import sys, os
from pyCBT.constants import DATADIR
from collections import OrderedDict
from ruamel_yaml import YAML
import oandapyV20
from oandapyV20.endpoints.accounts import AccountList

ATTRS = OrderedDict(
    environment=dict(default="practice", help="Server environment", choices=["practice", "live"]),
    port=dict(type=int, default=443, help="Server port"),
    ssl=dict(type=bool, default=True, help="Use SSL protocol?"),
    token=dict(help="API authorization token"),
    username=dict(help="Username of the account owner"),
    datetime_format=dict(default="RFC3339", help="Datetime format", choices=["RFC3339", "UNIX"])
)

class Config(object):
    def __init__(self, new=False, interactive=False, **cmd_kwargs):

        # use kwargs to set default values in self.account_attrs
        self.account_attrs = ATTRS
        for attr in cmd_kwargs:
            self.account_attrs[attr]["default"] = cmd_kwargs.get(attr)
        self.FILENAME = os.path.join(DATADIR, "providers/oanda/.oanda-account-{}.yml")
        # ask for environment (URL, choices: practice, live)
        self.environment = self.ask_choice(
            header="Available environments",
            choices=self.account_attrs["environment"]["choices"],
            default=self.account_attrs["environment"]["default"],
            question=self.account_attrs["environment"]["help"]
        )
        # ask for token
        self.token = self.ask_plain(
            header=self.account_attrs["token"]["help"],
            default=self.account_attrs["token"]["default"]
        )
        # get accounts
        self.accounts = self.get_accounts(self.token, self.environment)
        # ask for active account
        self.active_account = self.ask_choice(
            header="Available accounts",
            choices=self.accounts,
            question="Active account"
        )
        # if config file exist and not new
        self.filename = self.FILENAME.format(self.active_account)
        if os.path.isfile(self.filename) and not new:
        #   read account info
            self.from_file = self.get_from_file(self.filename)
        #   if interactive
            if interactive:
        #       ask for rest of parameters using config file as default values
                self.port = self.ask_plain(
                    header=self.account_attrs["port"]["help"],
                    default=self.from_file["port"],
                    dtype=type(self.from_file["port"])
                )
                self.ssl = self.ask_plain(
                    header=self.account_attrs["ssl"]["help"],
                    default=self.from_file["ssl"],
                    dtype=type(self.from_file["ssl"])
                )
                self.username = self.ask_plain(
                    header=self.account_attrs["username"]["help"],
                    default=self.from_file["username"]
                )
                self.datetime_format = self.ask_choice(
                    header="Available datetime formats",
                    choices=self.account_attrs["datetime_format"]["choices"],
                    question=self.account_attrs["datetime_format"]["help"],
                    default=self.from_file["datetime_format"]
                )
        #   else
            else:
        #       set rest of parameters using default values
                self.port = self.from_file["port"]
                self.ssl = self.from_file["ssl"]
                self.username = self.from_file["username"]
                self.datetime_format = self.from_file["datetime_format"]
        # else
        else:
        #   ask for rest of parameters
            self.port = self.ask_plain(
                header=self.account_attrs["port"]["help"],
                default=self.account_attrs["port"]["default"],
                dtype=self.account_attrs["port"]["type"]
            )
            self.ssl = self.ask_plain(
                header=self.account_attrs["ssl"]["help"],
                default=self.account_attrs["ssl"]["default"],
                dtype=self.account_attrs["ssl"]["type"]
            )
            self.username = self.ask_plain(
                header=self.account_attrs["username"]["help"]
            )
            self.datetime_format = self.ask_choice(
                header="Available datetime formats",
                choices=self.account_attrs["datetime_format"]["choices"],
                question=self.account_attrs["datetime_format"]["help"],
                default=self.account_attrs["datetime_format"]["default"]
            )
        # update self.info
        self.info = self.set_info()

    def ask_plain(self, header, default=None, dtype=None):

        print
        if default is None:
            value = raw_input("{}: ".format(header))
        else:
            value = raw_input("{} [{}]: ".format(header, default))
            if value == "": value = str(default)
        if dtype is None:
            return value
        else:
            value = eval(value)
            if not type(value) == dtype:
                raise TypeError("{} is not {} type".format(value, dtype))
            return value

    def ask_choice(self, header, choices, question, default=None, dtype=None):

        if len(choices)==1: default = choices[0]
        print
        print "{}:".format(header)
        for i, choice in enumerate(choices):
            print "[{}] {}".format(i+1, choice)
        if default is None:
            select = raw_input("{}: ".format(question))
        else:
            i_default = choices.index(default) + 1
            select = raw_input("{}? [{}]: ".format(question, i_default))
            if select == "":
                select = i_default - 1
            else:
                select = int(select) - 1
        if dtype is None:
            return choices[select]
        else:
            return dtype(choices[select])

    def get_accounts(self, token, environment):
        api = oandapyV20.API(access_token=token, environment=environment)
        r = AccountList()
        api.request(r)
        return [account["id"] for account in r.response["accounts"]]

    def get_from_file(self, filename):
        yaml = YAML()
        with open(filename, "r") as file:
            info = yaml.load(file)
        return info

    def set_to_file(self, filename):
        yaml = YAML()
        with open(filename, "w") as file:
            yaml.dump(self.info, file)

    def set_info(self):
        info = OrderedDict(zip(
        [
            "environment",
            "port",
            "ssl",
            "token",
            "username",
            "datetime_format",
            "accounts",
            "active_account"
        ],
        [
            self.environment,
            self.port,
            self.ssl,
            self.token,
            self.username,
            self.datetime_format,
            self.accounts,
            self.active_account
        ]))
        return info
