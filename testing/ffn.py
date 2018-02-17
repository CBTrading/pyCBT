import stockstats
import ffn
import fxchoice_data

from constants import *
from collections import OrderedDict

np = ffn.core.np
pd = ffn.data.pd
plt = ffn.core.plt

instruments = fxchoice_data.get_instruments()

for kw in instruments:
    print instruments[kw].head(5)
