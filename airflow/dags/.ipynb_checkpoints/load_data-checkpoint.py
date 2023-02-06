import pandas as pd
from sklearn import datasets
from sklearn.model_selection import train_test_split

df = pd.read_csv(r'dataset.csv', on_bad_lines='skip', delimiter=';')

# print(df.head(5))
df.describe()

print(len(df))


