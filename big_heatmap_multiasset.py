
## data : risk scores [0 to 1 scale]
## input file : Excel in /tmp folder here (with one spreadsheet)
## if there are more than 50 locations in the input file, then we only include the first 50 locations
## default: historical period

## this BIG heatmap compares risk score values between locations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def big_heatmap_multiasset(clrs, bins, labels,): 