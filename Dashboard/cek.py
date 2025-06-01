import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# Membaca file Customer
file_path = "full_orders.csv"
full_orders_df = pd.read_csv(file_path)

# Menampilkan 5 baris pertama
full_orders_df.info()


# Membaca file Customer
file_path = "full_products.csv"
full_products_df = pd.read_csv(file_path)

# Menampilkan 5 baris pertama
full_products_df.info()


# Membaca file Customer
file_path = "full_reviews.csv"
full_reviews_df = pd.read_csv(file_path)

# Menampilkan 5 baris pertama
full_reviews_df.info()
