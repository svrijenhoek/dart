import pandas as pd
import pickle
from pathlib import Path
import os

d = pd.read_pickle("data/output.pickle")

columns = list(d.columns)[2:9]
for i, column in enumerate(columns):
    _, d[column], _  = d[column].str

d.iloc[:,0:8].to_csv("data/output.csv")
