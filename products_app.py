from flask import Flask, render_template, url_for

from pyCBT.data.providers.oanda import historical
from pyCBT.data.providers.oanda import account

import oandapyV20
from oandapyV20.endpoints.accounts import AccountInstruments

# get account summary
config = account.Config()
account_summary = config.get_from_file()
# instantiate API client
api = oandapyV20.API(
    access_token=account_summary.pop("token"),
    environment=account_summary.pop("environment"),
    request_params={"timeout": account_summary.pop("timeout")}
)
# get tradeable instruments & define choices list
r = AccountInstruments(accountID=account_summary.get("active_account"))
api.request(r)
response = r.response.get("instruments")
# restructure response & filter unwanted fields
instruments = {"symbol": [], "name": [], "type": []}
for instrument in response:
    for kw in instrument:
        if kw == "displayName":
            instruments["name"] += [instrument[kw]]
        elif kw == "type":
            instruments["type"] += [instrument[kw]]
        elif kw == "name":
            instruments["symbol"] += [instrument[kw]]
        else:
            continue
# define defaults
default_instruments = {"candles": "WTICO_USD", "charts": ["EUR_USD", "USD_JPY", "GBP_USD", "XAU_USD"]}
default_resolutions = {"candles": "M15", "charts": "M15"}
default_datetimes = {"candles": ("2018-02-20", "2018-03-02"), "charts": ("2018-02-20", "2018-03-02")}
default_timezone = "America/New_York"

# initialize flask application
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html.j2")

@app.route("/products/", methods=["GET", "POST"])
def products():
    if request.method == "POST":
        pass
    #   get historical parameters from POST request
    #   update charts with input parameters
    #   update defaults to input parameters
    elif request.method == "GET":
        pass
    #   show charts for default historical values (now)
    candles = historical.Candles(
        instrument=default_instruments["candles"],
        resolution=default_resolutions["candles"],
        from_date=default_datetimes["candles"][0],
        to_date=default_datetimes["candles"][1],
        timezone=default_timezone
    )
    candles.as_dictionary()
    
    #   show the form for updating historical parameters

    return render_template("products.html.j2")

if __name__ == "__main__":
    app.run(debug=True)
