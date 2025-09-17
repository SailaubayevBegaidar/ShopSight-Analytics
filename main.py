import pandas as pd

# Load CSV
df = pd.read_csv("dataset/olist_customers_dataset.csv")
dt = pd.read_csv("dataset/olist_geolocation_dataset.csv")
# Show first rows
print(df.head())
print(dt.head())
