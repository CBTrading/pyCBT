import sys, os

from collections import OrderedDict
from ruamel_yaml import YAML
import oandapyV20
from oandapyV20.endpoints.accounts import AccountList
from pyCBT.constants import DATADIR

class Config(object):
    """Given a OANDA token generates config summary that can be stored as a file

    Generates a config summary given a series of OANDA account attributes.
    This summary can be stored in a file, loaded from a file or
    generated interactively by command line interaction.

    Parameters
    ----------
    **kwargs : dictionary, optional
        keyword attributes that can be passed through command line. Valid keys
        are:

        * environment: API url environment: 'practice' or 'live'.
        * timeout: lifetime of the pending request in seconds.
        * token: the access token given by OANDA.
        * username: the user holding the token.
        * timezone: timezone for series alignment.
        * datetime_format: format used for datetime strings: 'RFC3339' or 'UNIX'.
        * accounts: accounts registered for given a token.
        * active_account: currently used account.
    """

    def __init__(self, **kwargs):

        self.attr_names = [
            "environment",
            "timeout",
            "token",
            "username",
            "timezone",
            "datetime_format",
            "accounts",
            "active_account"
        ]
        self.attr_defaults = OrderedDict(zip(
            self.attr_names,
            [
                kwargs.pop("enviroment", "practice"),
                kwargs.pop("timeout", 1.0),
                kwargs.pop("token", None),
                kwargs.pop("username", None),
                kwargs.pop("timezone", "UTC"),
                kwargs.pop("datetime_format", "RFC3339"),
                kwargs.pop("accounts", None),
                kwargs.pop("active_account", None)
            ]
        ))
        self.attr_helps = OrderedDict(zip(
            self.attr_names,
            [
                "Server environment",
                "Timeout of the requests in seconds",
                "API authorization token",
                "Username of the account owner",
                "Timezone for series alignment",
                "Datetime format",
                "Accounts owned by user",
                "Currently active account"
            ]
        ))
        self.attr_types = OrderedDict(zip(
            self.attr_names,
            [
                None,
                float,
                None,
                None,
                None,
                None,
                list,
                None
            ]
        ))
        self.attr_choices = OrderedDict(zip(
            self.attr_names,
            [
                ("practice", "live"),
                None,
                None,
                None,
                None,
                ("RFC3339", "UNIX"),
                None,
                None
            ]
        ))

        self.environment = None
        self.timeout = None
        self.token = None
        self.username = None
        self.timezone = None
        self.datetime_format = None
        self.accounts = None
        self.active_account = None

        self.summary = None

        self._filename_template = os.path.join(DATADIR, "providers/oanda/.oanda-account-{}.yml")
        self._filename = None

    def update_defaults(self, **kwargs):
        """Update default attribute values to given keyword arguments
        """
        self.attr_defaults.update(kwargs)
        return None

    # ERROR: join ask_plain and ask choices to ease the looping
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

    def ask_choice(self, header, choices, question, default=None):
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
        # return selected choice
        return choices[select]

    def ask_account(self):
        """Ask for account attributes from command line
        """
        # ask for environment or use command line provided
        # ERROR: use a for loop to ask
        self.environment = self.ask_choice(
            header="Available environments",
            choices=self.attr_choices["environment"],
            default=self.attr_defaults["environment"],
            question=self.attr_helps["environment"]
        )
        # ask for token
        self.token = self.ask_plain(
            header=self.attr_helps["token"],
            default=self.attr_defaults["token"]
        )
        # get accounts
        api = oandapyV20.API(access_token=self.token, environment=self.environment)
        # generate request to appropriate endpoint
        r = AccountList()
        api.request(r)
        # store list of account IDs
        self.accounts = [account["id"] for account in r.response["accounts"]]
        # ask for active account
        self.active_account = self.ask_choice(
            header="Available accounts",
            choices=self.accounts,
            question=self.attr_helps["active_account"]
        )
        return None

    def ask_attributes(self):
        """Ask for attributes from command line
        """
        self.timeout = self.ask_plain(
            header=self.attr_helps["timeout"],
            default=self.attr_defaults["timeout"],
            dtype=self.attr_types["timeout"]
        )
        self.username = self.ask_plain(
            header=self.attr_helps["username"],
            default=self.attr_defaults["username"],
            dtype=self.attr_types["username"]
        )
        self.timezone = self.ask_plain(
            header=self.attr_helps["timezone"],
            default=self.attr_defaults["timezone"],
            dtype=self.attr_types["timezone"]
        )
        self.datetime_format = self.ask_choice(
            header="Available datetime formats",
            choices=self.attr_choices["datetime_format"],
            question=self.attr_helps["datetime_format"],
            default=self.attr_defaults["datetime_format"]
        )
        return None

    def set_account(self):
        """Set account attributes from defaults
        """
        self.environment = self.attr_defaults["environment"]
        self.token = self.attr_defaults["token"]
        self.active_account = self.attr_defaults["active_account"]
        return None

    def set_attributes(self):
        """Set attribute values from defults
        """
        self.timeout = self.attr_defaults["timeout"]
        self.username = self.attr_defaults["username"]
        self.datetime_format = self.attr_defaults["datetime_format"]
        return None

    def get_filename(self, account=None):
        """Return config filename
        """
        self._filename = self._filename_template.format(account)
        return self._filename

    def get_from_file(self, file):
        """Load config attributes from file
        """
        # instantiate yaml object
        yaml = YAML()
        # load config file
        summary = yaml.load(file)
        # return file content in dictionary
        return summary

    def set_summary(self):
        """Set config summary in dictionary
        """
        # define config summary dictionary
        self.summary = OrderedDict(zip(
            self.attr_names,
            [
                self.environment,
                self.timeout,
                self.token,
                self.username,
                self.timezone,
                self.datetime_format,
                self.accounts,
                self.active_account
            ]
        ))
        return None

    def set_to_file(self, file):
        """Dump config attributes to file

        This method requires that 'summary' is already set.
        """
        if self.summary is None:
            raise ValueError("You must define 'summary' first.")
        # instantiate yaml object
        yaml = YAML()
        # dump config summary in config file
        yaml.dump(self.summary, file)
        return None
