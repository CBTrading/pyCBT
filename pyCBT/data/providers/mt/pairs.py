def get_mt_pairs():
    """Returns MT pairs from DATA path"""
    import pandas as pd
    import os, pickle

    from collections import OrderedDict

    from pyCBT.constants import DATADIR, OHLCV

    data_path = os.path.join(DATADIR, "providers/mt")
    pickle_path = os.path.join(DATADIR, "pickles")

    try:
        pairs = pickle.load(open("{}/mt-pairs.p".format(pickle_path), "rb"))
    except IOError:
        filepaths = sorted([os.path.join(root, file)
                                for root, subs, files in os.walk(data_path)
                                    for file in files if file.endswith("M1.csv")])

        pairs = OrderedDict()
        for filepath in filepaths:
            filename = os.path.basename(filepath).split(".csv")[0][:-2]

            pairs[filename] = pd.read_csv(filepath, index_col=0, parse_dates=True,
                                          names=["DATE"]+OHLCV, usecols=["DATE"]+OHLCV)

            # ONLY FOR DEBUGGING
            # print
            # print filename
            # print pairs[filename].head(5)

        pickle.dump(pairs, open("{}/mt-pairs.p".format(pickle_path), "wb"))

    return pairs

if __name__ == "__main__":
    pairs = get_mt_pairs()

    for kw in pairs:
        print
        print kw
        print pairs[kw].head(5)
