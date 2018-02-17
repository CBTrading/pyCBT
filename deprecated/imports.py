import urllib, json
import pandas as pd

from ._constants import URL_EIA, KEY_EIA, IMPORT_SERIES_ID, DATADIR_EIA

url = URL_EIA.format(KEY_EIA, IMPORT_SERIES_ID)

res = urllib.urlopen(url)
data = json.loads(res.read())
table = data.get("series")[0].get("data")

imports = pd.DataFrame(data=table, columns="DATE IMPORTS".split())
imports["DATE"] = imports["DATE"].apply(lambda x: "{}-{}-{}".format(x[:4], x[4:6], x[6:]))
imports.to_csv("{}/eia-imports_mbbl-day.csv".format(DATADIR_EIA), index=False)
