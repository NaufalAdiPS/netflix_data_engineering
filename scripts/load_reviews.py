import pandas as pd
from sqlalchemy import create_engine

# koneksi postgres
engine = create_engine("postgresql://postgres:tanyamama123@localhost:5433/netflix_dw")

# load csv
df = pd.read_csv("data/raw/reviews.csv")

# insert ke postgres
df.to_sql("reviews", engine, schema="bronze", if_exists="replace", index=False)

print("SUCCESS LOAD data reviews")