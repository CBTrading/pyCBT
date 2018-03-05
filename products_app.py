from flask import Flask, render_template, url_for, request

from pyCBT.data.providers.oanda import historical
from pyCBT.data.providers.oanda import account

import oandapyV20
from oandapyV20.endpoints.accounts import AccountInstruments

# ERROR: implement this first block as a function and run it before app.run
# get account summary
client = account.Client()
# get tradeable instruments & define choices list
r = AccountInstruments(accountID=client.account_summary.get("account"))
client.api.request(r)
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
default_resolutions = {"candles": "H1", "charts": "H1"}
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
    else:
        pass
    #   show charts for default historical values (now)
        candles = historical.Candles(
            client=client,
            instrument=default_instruments["candles"],
            resolution=default_resolutions["candles"],
            from_date=default_datetimes["candles"][0],
            to_date=default_datetimes["candles"][1],
            datetime_fmt="JSON",
            timezone=default_timezone
        )
        candles = candles.as_dictionary()
        ohlc = []
        volume = []
        for i in xrange(len(candles["DATETIME"])):
            ohlc += [[
                candles["DATETIME"][i],
                candles["OPEN"][i],
                candles["HIGH"][i],
                candles["LOW"][i],
                candles["CLOSE"][i]
            ]]
            volume += [[
                candles["DATETIME"][i],
                candles["VOLUME"][i]
            ]]

    #   show the form for updating historical parameters

    return render_template(
        "products.html.j2",
        candles_symbol=instruments["name"][instruments["symbol"].index(default_instruments["candles"])],
        ohlc=ohlc,
        volume=volume
    )

if __name__ == "__main__":
    app.run(debug=True)
