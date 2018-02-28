import sys, os
from pyCBT.constants import DATADIR
from collections import OrderedDict
from ruamel_yaml import YAML
import oandapyV20
from oandapyV20.endpoints.accounts import AccountList

# ERROR: build dictionaries: attr_name, attr_default, attr_help, attr_type, attr_choices
ATTRS = OrderedDict(
    environment=dict(default="practice", help="Server environment", choices=["practice", "live"]),
    port=dict(type=int, default=443, help="Server port"),
    ssl=dict(type=bool, default=True, help="Use SSL protocol?"),
    token=dict(help="API authorization token"),
    username=dict(help="Username of the account owner"),
    datetime_format=dict(default="RFC3339", help="Datetime format", choices=["RFC3339", "UNIX"])
)

class Config(object):
    """Given a OANDA token generates config summary that can be stored as a file

    Generates a config summary given a series of OANDA account attributes.
    This summary can be stored in a file, loaded from a file or
    generated interactively by command line interaction.

    Parameters
    ----------
    new : boolean, optional
        start new config summary. Defaults to False.
    interactive : boolean, optional
        ask for user input while setting account attributes. Defaults to False
    **cmd_kwargs : dictionary, optional
        keyword attributes that can be passed through command line. Valid keys
        are:

        * environment: API url environment: 'practice' or 'live'.
        * port: port number for submmitting requests.
        * ssl: use SSL protocol or not.
        * token: the access token given by OANDA.
        * username: the user holding the token.
        * datetime_format: format used for datetime strings: 'RFC3339' or 'UNIX'.
    """

    def __init__(self, new=False, interactive=False, **cmd_kwargs):

        # ERROR: ask config info when requested not on init
        # use kwargs to set default values in self.account_attrs
        self.account_attrs = ATTRS
        for attr in cmd_kwargs:
        # ERROR: THIS BREAKS WHEN PASSING active_account ARGUMENT ----------------------------------
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
        #   else generate config from file without asking
            else:
        #       set rest of parameters using default values
                self.port = self.from_file["port"]
                self.ssl = self.from_file["ssl"]
                self.username = self.from_file["username"]
                self.datetime_format = self.from_file["datetime_format"]
        # else generate new config
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
        # define config summary
        self.info = self.set_info()

    # ERROR: define method for reading config file from account ID
    # ERROR: define method for asking config parameters from new or file (not) interactively
    def ask_plain(self, header, default=None, dtype=None):
        """Ask for user input for a given account attribute

        Parameters
        ----------
        header : string
            Description of the attribute.
        default : any, optional
            Default value for attribute.
        dtype : type object, optional
            Data type to cast value given by user.
        """

        print
        # if not default value present
        if default is None:
        #   ask for value
            value = raw_input("{}: ".format(header))
        # else if default value present
        else:
        #   ask for value with default value
            value = raw_input("{} [{}]: ".format(header, default))
        #   parse value from user
            if value == "": value = str(default)
        # if not given data type
        if dtype is None:
        #   return plain string with value
            return value
        # else if given data type
        else:
        #   evaluate given string value
            value = eval(value)
        #   check if given value is the same type as given
            if not type(value) == dtype:
        #       raise error if type mismatch
                raise TypeError("{} is not {} type".format(value, dtype))
            return value

    def ask_choice(self, header, choices, question, default=None, dtype=None):
        """Ask user to choose value for given attribute from several options

        Parameters
        ----------
        header : string
            Description of the choices.
        choices : list or tuple
            Choices for the given attribute.
        question : string
            Ask user to choose one of the options.
        default : any
            Default value for the attribute.
        dtype : type object, optional
            Data type to cast value given by user.
        """

        # if only one choice, make it default choice
        if len(choices)==1: default = choices[0]

        # display list of choices
        print
        print "{}:".format(header)
        for i, choice in enumerate(choices):
            print "[{}] {}".format(i+1, choice)
        # if not default choice present
        if default is None:
        #   ask for choice
            select = raw_input("{}: ".format(question))
        # else if default choice present
        else:
        #   define index of default choice
            i_default = choices.index(default) + 1
        #   ask for choice with default value
            select = raw_input("{}? [{}]: ".format(question, i_default))
        #   parse choice from user
            if select == "":
                select = i_default - 1
            else:
                select = int(select) - 1
        # if not given data type
        if dtype is None:
        #   return string with selected choice
            return choices[select]
        else:
        #   else cast selected choice to given type and return it
        # ERROR: try eval then raise error
        # ERROR: choices are already of the desired type
            return dtype(choices[select])

    def get_accounts(self, token, environment):
        """Get accounts from user token

        Parameters
        ----------
        token : string
            Access token given by OANDA.
        environment : string
            API url environment: 'practice' or 'live'.
        """

        # open API client
        api = oandapyV20.API(access_token=token, environment=environment)
        # generate request to appropriate endpoint
        r = AccountList()
        api.request(r)
        # return list of account IDs
        return [account["id"] for account in r.response["accounts"]]

    def get_from_file(self, filename):
        """Load config attributes from file

        Parameters
        ----------
        filename : string
            File path storing the config summary
        """

        # instantiate yaml object
        yaml = YAML()
        # load config file
        with open(filename, "r") as file:
            info = yaml.load(file)
        # return file content in dictionary
        return info

    def set_to_file(self, filename):
        """Dump config attributes to file

        Parameters
        ----------
        filename : string
            File path storing the config summary
        """

        # instantiate yaml object
        yaml = YAML()
        # dump config summary in config file
        with open(filename, "w") as file:
            yaml.dump(self.info, file)

    def set_info(self):
        """Set config summary in dictionary
        """

        # define config summary dictionary
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
