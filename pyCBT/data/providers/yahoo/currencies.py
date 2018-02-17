def get_pairs():
    import ffn, pickle, time, os

    from constants import OHLCV, CURRENCY_TICKERS, PAIRS
    from string import join
    from collections import OrderedDict

    t = time.localtime()
    I_DATE, F_DATE = "2007-01-01", "{}-{}-{}".format(t.tm_year, t.tm_mon, t.tm_mday)

    DATA_DIR = "data"
    try:
        os.stat(DATA_DIR)
    except:
        os.mkdir(DATA_DIR)

    # GET SOME PAIRS
    try:
        # try loading binary object if exists
        pairs = pickle.load(open("{}/pairs.p".format(DATA_DIR), "rb"))
    except IOError:
        # initialize pairs dictionary
        pairs = OrderedDict()
        for i, ticker_name in enumerate(CURRENCY_TICKERS):
            # download pairs from YAHOO
            ticker = join(["{}:{}".format(ticker_name, col) for col in OHLCV], ",")
            pairs[PAIRS[i]] = ffn.get(ticker, start=I_DATE, end=F_DATE, column_names=OHLCV)
            print pairs[PAIRS[i]].head(5)
            # save pairs to csv files
            pairs[PAIRS[i]].to_csv("{}/{}.csv".format(DATA_DIR, ticker_name.replace("=", "-").lower()), index_label="Date")
        # save binary object for later runs (useful for limited internet connections)
        pickle.dump(pairs, open("{}/pairs.p".format(DATA_DIR), "wb"))

    return pairs

if __name__ == "__main__":
    pairs = get_pairs()

    for kw in pairs:
        print pairs[kw].head(5)
