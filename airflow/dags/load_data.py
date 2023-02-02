import pandas as pd

df = pd.read_csv(r'dataset.csv', on_bad_lines='skip', delimiter=';')
print(df.shape)