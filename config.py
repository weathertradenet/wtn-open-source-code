import os
import pandas as pd

clrs = ["#709386", "#C9C17B", "#CE9D61", "#E2432D", "#B50F0B"]
bins = [0, 0.19, 0.39, 0.59, 0.79, 1]
labels = ['Low', 'Moderate', 'High', 'Severe', 'Extreme']


CHOICES_HAZARDS = {
    'FD': 'River Flood',
    'SL': 'Coastal Flood',    
    'LS': 'Landslide',
    'ER': 'Extreme Rainfall',
    'SS': 'Severe Storm',
    'WF': 'Wildfire',
    'DR': 'Drought',
    'HW': 'Heat Wave',
    'CS': 'Cold Stress',
    'TC': 'Temp Change',
    'PC': 'Precip Change',    
    'AL': 'Overall Hazard'
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
