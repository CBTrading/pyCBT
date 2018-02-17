# EIA URL
URL_EIA = "http://api.eia.gov/series/?api_key={}&series_id={}"
# EIA API KEY
KEY_EIA = "81c6769f3597f44ca2cf3a097f2a51ff"

# EIA DATA SERIES ID
IMPORT_SERIES_ID = "PET.WCRIMUS2.W"
EXPORT_SERIES_ID = "PET.WCREXUS2.W"
PRODUCTION_SERIES_ID = "PET.MCRFPUS1.M"
STOCKS_SERIES_ID = "PET.WCRSTUS1.W"

# EIA DATA PATH
import os
from pyCBT.constants import DATADIR

DATADIR_EIA = os.path.join(DATADIR, "providers/eia")
