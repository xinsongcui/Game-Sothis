import pandas as pd
import json

f = open('data.json')
data = json.load(f)
f.close()

df = pd.read_json (r'data.json')
df.to_csv(r'data.csv')