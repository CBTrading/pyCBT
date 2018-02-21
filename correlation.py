# input parameters: TIME_FRAME, PRICE, VOLUME, PAIRS
# procedure
# load data
# trim data to relevant time frame
# compute correlations
# draw correlation map
# return ffn/plt figure (if main)
# return Highcharts object (if module)
import ffn

from collections import OrderedDict
from itertools import product
from pyCBT.data.providers.mt.pairs import get_mt_pairs

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

# define constants
# time frame in periods/minutes (because data is sampled in minutes)
TIME_FRAME = 30
# define target price
PRICE = "CLOSE"
# define volume column
VOLUME = "VOLUME"

pairs = get_mt_pairs()

PAIRS = pairs.keys()[:10]

# extract price for each instrument
price = pd.DataFrame(index=range(5*TIME_FRAME))
for pair_name in PAIRS:
    price[pair_name] = pairs[pair_name].filter(like=PRICE).values[-5*TIME_FRAME:]

# compute correlations
C = pd.DataFrame(data=np.nan, index=PAIRS, columns=PAIRS)
for i, j in product(range(len(PAIRS)), range(len(PAIRS))):
    price_i, price_j = price[PAIRS[i]][-TIME_FRAME:].values, price[PAIRS[j]][-TIME_FRAME:].values
    C.loc[PAIRS[i]][PAIRS[j]] = np.corrcoef(price_i, price_j)[1, 0]

ffn.core.plot_heatmap(C, cmap="Spectral", title="Correlations")
plt.show()
