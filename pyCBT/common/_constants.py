from collections import OrderedDict

financial_symbols = [
    "S&P 500",
    "DAX",
    "DJA",
    "DJI",
    "DXY",
    "FCHI",
    "FTSE",
    "HSI",
    "NASDAQ",
    "NYA",
    "Nikkei",
    "SSE",
    "VIX",
    "VXN",
    "VXO",
    "Consumer disc.",
    "Consumer stap.",
    "Energy",
    "Financials",
    "Health care",
    "Industrials",
    "Inf. tech.",
    "Materials",
    "Real state",
    "Utilities",
    "AAPL",
    "AMZN",
    "BRK-B",
    "FB",
    "GOOG",
    "JNJ",
    "JPM",
    "MSFT",
    "XOM",
    "Crude oil",
    "Gold",
    "EURUSD",
    "GBPUSD",
    "USDCAD",
    "USDCNY",
    "USDJPY"
]
economical_symbols = [
    "ADP nonfarm employment",
    "Average hourly earnings",
    "CB consumer confidence",
    "Core CPI",
    "GDP",
    "Interest rate decision",
    "Nonfarm payrolls",
    "PPI",
    "Unemployment rate"
]
url_params = [
    {"category": "indices", "instrument": "us-spx-500"},
    {"category": "indices", "instrument": "germany-30"},
    {"category": "indices", "instrument": "dj-composite-average"},
    {"category": "indices", "instrument": "us-30"},
    {"category": "indices", "instrument": "usdollar"},
    {"category": "indices", "instrument": "france-40"},
    {"category": "indices", "instrument": "uk-100"},
    {"category": "indices", "instrument": "hang-sen-40"},
    {"category": "indices", "instrument": "nasdaq-composite"},
    {"category": "indices", "instrument": "nyse-composite"},
    {"category": "indices", "instrument": "japan-ni225"},
    {"category": "indices", "instrument": "shanghai-composite"},
    {"category": "indices", "instrument": "volatility-s-p-500"},
    {"category": "indices", "instrument": "cboe-nasdaq-100-voltility"},
    {"category": "indices", "instrument": "cboe-oex-implied-volatility"},
    {"category": "indices", "instrument": "s-p-500-consumer-discretionary"},
    {"category": "indices", "instrument": "s-p-500-consumer-staples"},
    {"category": "indices", "instrument": "s-p-500-energy"},
    {"category": "indices", "instrument": "s-p-500-financial"},
    {"category": "indices", "instrument": "s-p-500-health-care"},
    {"category": "indices", "instrument": "s-p-500-industrials"},
    {"category": "indices", "instrument": "s-p-500-information-technology"},
    {"category": "indices", "instrument": "s-p-500-materials"},
    {"category": "indices", "instrument": "s-p-500-telecom-services"},
    {"category": "indices", "instrument": "s-p-500-utilities"},
    {"category": "equities", "instrument": "apple-computer-inc"},
    {"category": "equities", "instrument": "amazon-com-inc"},
    {"category": "equities", "instrument": "berkshire-hathaway"},
    {"category": "equities", "instrument": "facebook-inc"},
    {"category": "equities", "instrument": "google-inc-c"},
    {"category": "equities", "instrument": "johnson-johnson"},
    {"category": "equities", "instrument": "jp-morgan-chase"},
    {"category": "equities", "instrument": "microsoft-corp"},
    {"category": "equities", "instrument": "exxon-mobil"},
    {"category": "commodities", "instrument": "crude-oil"},
    {"category": "commodities", "instrument": "gold"},
    {"category": "currencies", "instrument": "eur-usd"},
    {"category": "currencies", "instrument": "gbp-usd"},
    {"category": "currencies", "instrument": "usd-cad"},
    {"category": "currencies", "instrument": "usd-cny"},
    {"category": "currencies", "instrument": "usd-jpy"},
    {"category": "economic-calendar", "instrument": "adp-nonfarm-employment-change-1"},
    {"category": "economic-calendar", "instrument": "average-hourly-earnings-8"},
    {"category": "economic-calendar", "instrument": "cb-consumer-confidence-48"},
    {"category": "economic-calendar", "instrument": "core-cpi-56"},
    {"category": "economic-calendar", "instrument": "gdp-375"},
    {"category": "economic-calendar", "instrument": "interest-rate-decision-168"},
    {"category": "economic-calendar", "instrument": "nonfarm-payrolls-227"},
    {"category": "economic-calendar", "instrument": "ppi-238"},
    {"category": "economic-calendar", "instrument": "unemployment-rate-300"}
]
indicator_names = financial_symbols + economical_symbols
features_params = OrderedDict(zip(indicator_names, url_params))

extra_columns = ["Class", "Year", "Month", "DayWeek"]
return_names = map(lambda symbol: "{} return".format(symbol), financial_symbols)
features_names_price = financial_symbols + economical_symbols
features_names_return =  return_names + economical_symbols
