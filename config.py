import os
import pandas as pd

clrs = ["#3b6946", "#aeb15a", "#b17829", "#8a4a18", "#7a1f1f"]
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
    'ER': 'Extreme<br>Rainfall',
    'TC': 'Temperature<br>Change',
    'PC': 'Precipitation<br>Change',
    'SL': 'Coastal Flood',
    'FD': 'River Flood'
}

