import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

# Set style for plots
sns.set_style("whitegrid")

# --- Judul Aplikasi ---
st.set_page_config(layout="wide")
st.title("📦 Proyek Analisis Data: E-Commerce Public Dataset Brazil 🇧🇷")

st.markdown("<h4 style='color:#4F8BF9;'>Selamat datang di dashboard interaktif E-Commerce Brazil! 🎉</h4>",
            unsafe_allow_html=True)
st.divider()


@st.cache_data
def load_data():
    try:
        full_orders_df = pd.read_csv("Dashboard/full_orders.csv")
        full_products_df = pd.read_csv("Dashboard/full_products.csv")
        full_reviews_df = pd.read_csv("Dashboard/full_reviews.csv")

        # Pastikan kolom datetime diubah tipenya jika diperlukan untuk analisis lebih lanjut
        full_orders_df['order_purchase_timestamp'] = pd.to_datetime(
            full_orders_df['order_purchase_timestamp'])

        return full_orders_df, full_products_df, full_reviews_df
    except FileNotFoundError:
        st.error("❗ Pastikan file 'full_orders.csv', 'full_products.csv', dan 'full_reviews.csv' tersedia di folder 'Dashboard/'.")
        st.stop()  # Hentikan eksekusi jika file tidak ditemukan


full_orders_df, full_products_df, full_reviews_df = load_data()

st.sidebar.header("🔎 Filter Data")
min_date = full_orders_df['order_purchase_timestamp'].min().date()
max_date = full_orders_df['order_purchase_timestamp'].max().date()
date_range = st.sidebar.date_input(
    "Pilih Rentang Tanggal Order",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
    # Filter orders
    filtered_orders_df = full_orders_df[
        (full_orders_df['order_purchase_timestamp'].dt.date >= start_date) &
        (full_orders_df['order_purchase_timestamp'].dt.date <= end_date)
    ]
    # Filter products & reviews berdasarkan order_id yang lolos filter
    filtered_products_df = full_products_df[full_products_df['order_id'].isin(
        filtered_orders_df['order_id'])]
    filtered_reviews_df = full_reviews_df[full_reviews_df['order_id'].isin(
        filtered_orders_df['order_id'])]
else:
    filtered_orders_df = full_orders_df
    filtered_products_df = full_products_df
    filtered_reviews_df = full_reviews_df

# --- FITUR INTERAKTIF: FILTER KATEGORI PRODUK ---
all_categories = filtered_products_df['product_category_name_english'].dropna(
).unique()
selected_categories = st.sidebar.multiselect(
    "Pilih Kategori Produk (opsional, bisa lebih dari satu):",
    options=sorted(all_categories),
    default=sorted(all_categories)  # default: semua kategori
)

if selected_categories:
    filtered_products_df = filtered_products_df[filtered_products_df['product_category_name_english'].isin(
        selected_categories)]
    # Filter reviews & orders berdasarkan order_id produk yang lolos filter kategori
    filtered_order_ids = filtered_products_df['order_id'].unique()
    filtered_reviews_df = filtered_reviews_df[filtered_reviews_df['order_id'].isin(
        filtered_order_ids)]
    filtered_orders_df = filtered_orders_df[filtered_orders_df['order_id'].isin(
        filtered_order_ids)]

# --- Pertanyaan Bisnis 1: Siapa Pelanggan Kita? ---
st.header("1. Siapa Pelanggan Kita? 👥")
st.info("""
Untuk mengetahui siapa pelanggan kita, kita akan menganalisis distribusi demografi pelanggan berdasarkan negara bagian dan kota, serta melihat karakteristik pembelian (jumlah pesanan dan total pengeluaran) di setiap wilayah tersebut. 🌎
""")

# Pre-calculate data for customer analysis (from your EDA)
customer_summary = filtered_orders_df.groupby('customer_unique_id').agg(
    total_orders=('order_id', 'nunique'),
    total_spend=('total_order_spend', 'sum'),
    customer_state=('customer_state', 'first'),
    customer_city=('customer_city', 'first')
).reset_index()

state_customer_analysis = customer_summary.groupby('customer_state').agg(
    num_unique_customers=('customer_unique_id', 'nunique'),
    total_orders_placed=('total_orders', 'sum'),
    total_revenue=('total_spend', 'sum'),
    avg_orders_per_customer=('total_orders', 'mean'),
    avg_spend_per_customer=('total_spend', 'mean')
).sort_values(by='num_unique_customers', ascending=False).reset_index()

city_customer_analysis = customer_summary.groupby('customer_city').agg(
    num_unique_customers=('customer_unique_id', 'nunique'),
    total_orders_placed=('total_orders', 'sum'),
    total_revenue=('total_spend', 'sum'),
    avg_orders_per_customer=('total_orders', 'mean'),
    avg_spend_per_customer=('total_spend', 'mean')
).sort_values(by='num_unique_customers', ascending=False).reset_index()

st.subheader("📍 Distribusi Pelanggan Berdasarkan Negara Bagian")
col1, col2 = st.columns(2)
with col1:
    st.write("🏆 **Top 10 Negara Bagian Berdasarkan Jumlah Pelanggan Unik:**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='num_unique_customers',
        y='customer_state',
        data=state_customer_analysis.head(10),
        palette=sns.color_palette("Blues", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title('Top 10 Negara Bagian Berdasarkan Jumlah Pelanggan Unik')
    ax.set_xlabel('Jumlah Pelanggan Unik')
    ax.set_ylabel('Negara Bagian')
    st.pyplot(fig)

with col2:
    st.write("💰 **Top 10 Negara Bagian Berdasarkan Total Pendapatan:**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='total_revenue',
        y='customer_state',
        data=state_customer_analysis.head(10).sort_values(
            by='total_revenue', ascending=False),
        palette=sns.color_palette("Oranges", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title('Top 10 Negara Bagian Berdasarkan Total Pendapatan')
    ax.set_xlabel('Total Pendapatan')
    ax.set_ylabel('Negara Bagian')
    st.pyplot(fig)

st.subheader("🏙️ Distribusi Pelanggan Berdasarkan Kota")
col3, col4 = st.columns(2)
with col3:
    st.write("🏆 **Top 10 Kota Berdasarkan Jumlah Pelanggan Unik:**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='num_unique_customers',
        y='customer_city',
        data=city_customer_analysis.head(10),
        palette=sns.color_palette("Blues", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title('Top 10 Kota Berdasarkan Jumlah Pelanggan Unik')
    ax.set_xlabel('Jumlah Pelanggan Unik')
    ax.set_ylabel('Kota')
    st.pyplot(fig)

with col4:
    st.write("💰 **Top 10 Kota Berdasarkan Total Pendapatan:**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='total_revenue',
        y='customer_city',
        data=city_customer_analysis.head(10).sort_values(
            by='total_revenue', ascending=False),
        palette=sns.color_palette("Oranges", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title('Top 10 Kota Berdasarkan Total Pendapatan')
    ax.set_xlabel('Total Pendapatan')
    ax.set_ylabel('Kota')
    st.pyplot(fig)

st.divider()

# --- Pertanyaan Bisnis 2: Produk & Penjual ---
st.header("2. Produk Apa yang Paling Diminati dan Menguntungkan, serta Bagaimana Performa Penjual Terkait Produk Tersebut? 🛒💸")

st.subheader("A. Analisis Kinerja Produk 📦")
st.info("""
Kita akan melihat kategori produk apa yang paling populer (berdasarkan jumlah pesanan) dan paling menguntungkan (berdasarkan total pendapatan). 📊
""")

# Pre-calculate data for product analysis (from your EDA)
category_performance = filtered_products_df.groupby('product_category_name_english').agg(
    num_orders=('order_id', 'nunique'),
    total_revenue=('item_total_price_with_freight', 'sum')
).reset_index()

top_popular_categories = category_performance.sort_values(
    by='num_orders', ascending=False).head(10)

top_profitable_categories = category_performance.sort_values(
    by='total_revenue', ascending=False).head(10)

col5, col6 = st.columns(2)
with col5:
    st.write(
        "🔥 **Top 10 Kategori Produk Paling Diminati (Berdasarkan Jumlah Pesanan):**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='num_orders',
        y='product_category_name_english',
        data=top_popular_categories,
        palette=sns.color_palette("Blues", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title('Top 10 Kategori Produk Paling Diminati (Jumlah Pesanan)')
    ax.set_xlabel('Jumlah Pesanan')
    ax.set_ylabel('Kategori Produk')
    st.pyplot(fig)

with col6:
    st.write(
        "💵 **Top 10 Kategori Produk Paling Menguntungkan (Berdasarkan Total Pendapatan):**")

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='total_revenue',
        y='product_category_name_english',
        data=top_profitable_categories,
        palette=sns.color_palette("Oranges", n_colors=10)[::-1],
        ax=ax
    )
    ax.set_title(
        'Top 10 Kategori Produk Paling Menguntungkan (Total Pendapatan)')
    ax.set_xlabel('Total Pendapatan')
    ax.set_ylabel('Kategori Produk')
    st.pyplot(fig)

st.subheader("B. Analisis Performa Penjual dan Distribusi Ulasan 🏪⭐")
st.info("""
Kita akan melihat bagaimana distribusi skor ulasan pelanggan dan mengidentifikasi penjual dengan performa terbaik dan terburuk berdasarkan ulasan. 📝
""")

# Visualisasi Distribusi Skor Ulasan
st.write("⭐ **Distribusi Skor Ulasan Pelanggan:**")
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(
    x='review_score',
    data=filtered_reviews_df,
    palette='Greens',
    order=sorted(filtered_reviews_df['review_score'].unique()),
    ax=ax
)
ax.set_title('Distribusi Skor Ulasan Pelanggan')
ax.set_xlabel('Skor Ulasan (1 = Terburuk, 5 = Terbaik)')
ax.set_ylabel('Jumlah Ulasan')
st.pyplot(fig)

# Pre-calculate data for seller performance (from your EDA)
seller_performance = filtered_reviews_df.groupby('seller_id').agg(
    average_review_score=('review_score', 'mean'),
    num_reviews=('review_score', 'count'),
    total_sales_value=('item_total_price_with_freight', 'sum')
).reset_index()

col7, col8 = st.columns(2)
with col7:
    st.write(
        "🏅 **Top 10 Penjual dengan Jumlah Review Terbanyak & Skor Ulasan Tinggi:**")
    top_10_sellers_by_score_and_reviews = seller_performance.sort_values(
        ['average_review_score', 'num_reviews'], ascending=[False, False]
    ).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='num_reviews',
        y='seller_id',
        data=top_10_sellers_by_score_and_reviews.sort_values(
            'num_reviews', ascending=False),
        palette='Greens',
        ax=ax
    )
    ax.set_title(
        'Top 10 Penjual dengan Jumlah Review Terbanyak & Skor Ulasan Tinggi')
    ax.set_xlabel('Jumlah Review')
    ax.set_ylabel('Seller ID')
    st.pyplot(fig)

with col8:
    st.write(
        "⚠️ **10 Penjual dengan Skor Ulasan Terendah & Jumlah Review Terbanyak:**")
    lowest_score_highest_reviews = seller_performance.sort_values(
        ['average_review_score', 'num_reviews'], ascending=[True, False]
    ).head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        x='num_reviews',
        y='seller_id',
        data=lowest_score_highest_reviews.sort_values(
            'num_reviews', ascending=False),
        palette='Reds',
        ax=ax
    )
    ax.set_title(
        '10 Penjual dengan Skor Ulasan Terendah & Jumlah Review Terbanyak')
    ax.set_xlabel('Jumlah Review')
    ax.set_ylabel('Seller ID')
    st.pyplot(fig)

st.divider()
