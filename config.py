import os
import pandas as pd

# clrs = ["#3b6946", "#aeb15a", "#b17829", "#8a4a18", "#7a1f1f"]
clrs = ["#709386", "#C9C17B", "#CE9D61", "#E2432D", "#B50F0B"]
bins = [0, 0.19, 0.39, 0.59, 0.79, 1]
labels = ['Low', 'Moderate', 'High', 'Severe', 'Extreme']


CHOICES_HAZARDS = {
    'AL': 'Overall Hazard',
    'CS': 'Cold Stress',
    'HW': 'Heat Wave',
    'LS': 'Landslide',
    'WF': 'Wildfire',
    'DR': 'Drought',
    'SS': 'Severe Storm',
    'ER': 'Extr Rainfall',
    'TC': 'Temp Change',
    'PC': 'Precip Change',
    'SL': 'Coastal Flood',
    'FD': 'River Flood'
}

period_mapping = {
    '2011-2020': 'hist',
    '2021-2030': '2030',
    '2031-2040': '2040',
    '2041-2050': '2050'
}

scenario_mapping = {
    'ssp126': 'RCP2.6',
    'ssp245': 'RCP4.5',
    'ssp585': 'RCP8.5'
}
