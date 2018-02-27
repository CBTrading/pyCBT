import os, yaml
from pyCBT.constants import DATADIR
from collections import OrderedDict


class Config(object):
    def __init__(self, new=False, interactive=False):

        self.CONF_FILE = os.path.join(DATADIR, "providers/oanda/.oanda-account-{}.yml")
        self.account_attrs = OrderedDict(
            hostname=dict(default="api-fxpractice.oanda.com", help="Server hostname"),
            streaming_hostname=dict(default="stream-fxpractice.oanda.com", help="Streaming server hostname"),
            port=dict(type=int, default=443, help="Server port"),
            ssl=dict(type=bool, default=True, help="Use SSL protocol?"),
            token=dict(help="API authorization token"),
            username=dict(help="Username of the account owner"),
            datetime_format=dict(default="RFC3339", help="Datetime format", choices=["RFC3339", "UNIX"]),
            accounts=dict(help="List of accounts owned by user"),
            active_account=dict(help="Active account")
        )
        # ask for hostname
        self.hostname = self.ask_plain(
            header=self.account_attrs["hostname"]["help"],
            default=self.account_attrs["hostname"]["default"]
        )
        # ask for token
        self.token = self.ask_plain(header=self.account_attrs["token"]["help"])
        # get accounts
        self.accounts = self.get_accounts(self.token)
        # ask for active account
        self.active_account = self.ask_choice(
            header="Available accounts",
            choices=self.accounts,
            question=self.account_attrs["active_account"]["help"]
        )
        # if config file exist and not new
        self.config_file = self.CONF_FILE.format(self.active_account)
        if os.path.isfile(self.config_file) and not new:
        #   read account info
            self.from_file = self.get_from_file(self.config_file)
        #   if interactive
            if interactive:
        #       ask for rest of parameters using config file as default values
                self.streaming_hostname = self.ask_plain(
                    header=self.account_attrs["streaming_hostname"]["help"],
                    default=self.from_file["streaming_hostname"]
                )
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
                    default=self.from_file["ssl"]
                )
                self.datetime_format = self.ask_choice(
                    header="Available datetime formats",
                    choices=self.account_attrs["datetime_format"]["choices"],
                    question=self.account_attrs["datetime_format"]["help"],
                    default=self.from_file["datetime_format"]
                )
        # else
        else:
        #   ask for rest of parameters
            self.streaming_hostname = self.ask_plain(
                header=self.account_attrs["streaming_hostname"]["help"],
                default=self.account_attrs["streaming_hostname"]["default"]
            )
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
            value = raw_input("{}: ".format(doc))
        else:
            value = raw_input("{} [{}]: ".format(doc, default))
            if value == "": value = default
        if dtype is None:
            return value
        else:
            return dtype(value)

    def ask_choice(self, header, choices, question, default=None, dtype=None):

        i_default = choices.index(default)+1
        print
        print ":".format(header)
        for i, choice in enumerate(choices):
            print "[{}] {}".format(i+1, choice)
        if default if None:
            select = raw_input("{}: ".format(question))
        else:
            select = raw_input("{}? [{}]: ".format(question, i_default))
        if select == "":
            select = i_default-1
        else:
            select = int(select)
        if dtype is None:
            return choices[select]
        else:
            return dtype(choices[select])

    def get_accounts(self, token):
        api = oandapyV20.API(access_token=self.token)
        r = AccountList()
        api.request(r)
        return [account["id"] for account in r.response["accounts"]]

    def get_from_file(self, filename):
        return yaml.load(filename)

    def set_info(self):
        return OrderedDict(
            hostname=self.hostname,
            streaming_hostname=self.streaming_hostname,
            port=self.port,
            ssl=self.ssl,
            token=self.token,
            username=self.username,
            datetime_format=self.datetime_format,
            accounts=self.accounts,
            active_account=self.active_account
        )
