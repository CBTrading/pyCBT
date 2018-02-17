def get_instruments():
    import ffn, pickle, time, os

    from constants import OHLCV, TICKERS, SYMBOLS
    from string import join
    from collections import OrderedDict

    t = time.localtime()
    I_DATE, F_DATE = "2007-01-01", "{}-{}-{}".format(t.tm_year, t.tm_mon, t.tm_mday)

    DATA_DIR = "data"
    try:
        os.stat(DATA_DIR)
    except:
        os.mkdir(DATA_DIR)

    # GET SOME INSTRUMENTS
    try:
        # try loading binary object if exists
        instruments = pickle.load(open("{}/instruments.p".format(DATA_DIR), "rb"))
    except IOError:
        # initialize instruments dictionary
        instruments = OrderedDict()
        for i, ticker in enumerate(TICKERS):
            # download instruments from YAHOO
            tickers = join(["{}:{}".format(ticker, col) for col in OHLCV], ",")
            instruments[SYMBOLS[i]] = ffn.get(tickers, start=I_DATE, end=F_DATE, column_names=OHLCV)
            print instruments[SYMBOLS[i]].head(5)
            # save instruments to csv files
            instruments[SYMBOLS[i]].to_csv("{}/{}.csv".format(DATA_DIR, SYMBOLS[i].strip(".").lower()), index_label="Date")
        # save binary object for later runs (useful for limited internet connections)
        pickle.dump(instruments, open("{}/instruments.p".format(DATA_DIR), "wb"))

    return instruments

if __name__ == "__main__":
    instruments = get_instruments()

    for kw in instruments:
        print instruments[kw].head(5)
