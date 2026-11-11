import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Afficionado Coffee Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("Afficionado Coffee Roasters clean.xlsx")
    return df

df = load_data()

st.title("Afficionado Coffee Roasters - Product Intelligence Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

categories = st.sidebar.multiselect(
    "Category",
    options=df["product_category"].unique(),
    default=df["product_category"].unique()
)

product_types = st.sidebar.multiselect(
    "Product Type",
    options=df["product_type"].unique(),
    default=df["product_type"].unique()
)

locations = st.sidebar.multiselect(
    "Store Location",
    options=df["store_location"].unique(),
    default=df["store_location"].unique()
)

top_n = st.sidebar.slider("Top N Products", min_value=5, max_value=30, value=10)

# Filter data
filtered_df = df[
    (df["product_category"].isin(categories)) &
    (df["product_type"].isin(product_types)) &
    (df["store_location"].isin(locations))
]

# KPIs
total_revenue = filtered_df["Revenue"].sum()
total_quantity = filtered_df["transaction_qty"].sum()
total_products = filtered_df["product_detail"].nunique()
avg_revenue = filtered_df["Revenue"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Total Quantity Sold", f"{total_quantity:,.0f}")
col3.metric("Unique Products", f"{total_products}")
col4.metric("Avg Revenue per Row", f"${avg_revenue:,.2f}")

st.markdown("---")

# Top Products by Revenue
st.subheader(f"Top {top_n} Products by Revenue")

top_products = (
    filtered_df.groupby("product_detail")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(top_n)
    .reset_index()
)

fig_bar = px.bar(
    top_products,
    x="Revenue",
    y="product_detail",
    orientation="h",
    title=f"Top {top_n} Products by Revenue",
    labels={"product_detail": "Product", "Revenue": "Revenue ($)"}
)
fig_bar.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_bar, use_container_width=True)

# Category Revenue
st.subheader("Revenue by Category")

category_rev = (
    filtered_df.groupby("product_category")["Revenue"]
    .sum()
    .reset_index()
)

fig_pie = px.pie(
    category_rev,
    values="Revenue",
    names="product_category",
    hole=0.4,
    title="Category Revenue Share"
)
st.plotly_chart(fig_pie, use_container_width=True)

# Scatter: Quantity vs Revenue
st.subheader("Popularity vs Revenue")

scatter_data = (
    filtered_df.groupby("product_detail")
    .agg({
        "transaction_qty": "sum",
        "Revenue": "sum"
    })
    .reset_index()
)

fig_scatter = px.scatter(
    scatter_data,
    x="transaction_qty",
    y="Revenue",
    size="Revenue",
    color="Revenue",
    hover_name="product_detail",
    title="Quantity Sold vs Revenue",
    labels={
        "transaction_qty": "Total Quantity Sold",
        "Revenue": "Total Revenue ($)"
    }
)
st.plotly_chart(fig_scatter, use_container_width=True)

# Product Performance Table
st.subheader("Product Performance Table")

table_data = (
    filtered_df.groupby("product_detail")
    .agg({
        "transaction_qty": "sum",
        "Revenue": "sum"
    })
    .reset_index()
    .sort_values("Revenue", ascending=False)
)

table_data["Revenue Share %"] = (table_data["Revenue"] / table_data["Revenue"].sum() * 100).round(2)

st.dataframe(table_data, use_container_width=True)
