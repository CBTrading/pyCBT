import os

# PATHS
BASEDIR = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(BASEDIR, "DATA")

# FILES
OHLCV = "OPEN HIGH LOW CLOSE VOLUME".split()

# YAHOO TICKERS & SYMBOLS
TICKERS = "^NDX ^GSPC ^N225 ^GDAXI ^FTSE ^DJI".split()
SYMBOLS = "USTECHIndex US500Index JAPANIndex DE30Index UK100Index US30Index".split()
# TICKERS = "^NDX ^GSPC ^N225 ^GDAXI ^FTSE ^DJI ^BCOMCL ^BCOMCO DXY.AT".split()
# SYMBOLS = "USTECHIndex US500Index JAPANIndex DE30Index UK100Index US30Index .WTICrude .BrentCrud DXY".split()

CURRENCIES = sorted("JPY EUR GBP AUD CAD CHF NZD XAG XAU".split())
CURRENCY_TICKERS = ["{}=X".format(currency) for currency in CURRENCIES]
PAIRS = ["USD/{}".format(currency) for currency in CURRENCIES]
