import urllib, json
import pandas as pd

from ._constants import URL_EIA, KEY_EIA, IMPORT_SERIES_ID, DATADIR_EIA

url = URL_EIA.format(KEY_EIA, PRODUCTION_SERIES_ID)

res = urllib.urlopen(url)
data = json.loads(res.read())
table = data.get("series")[0].get("data")

production = pd.DataFrame(data=table, columns="DATE PRODUCTION".split())
production["DATE"] = production["DATE"].apply(lambda x: "{}-{}".format(x[:4], x[4:]))
production["DATE"] = pd.to_datetime(production["DATE"])
production.to_csv("{}/eia-production_mbbl.csv".format(DATADIR_EIA), index=False)
