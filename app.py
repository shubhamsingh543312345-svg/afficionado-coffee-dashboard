import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(
    page_title="Afficionado Coffee Roasters",
    page_icon="☕",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_excel("Afficionado Coffee Roasters clean.xlsx")
    return df

df = load_data()

# Title
st.title("☕ Afficionado Coffee Roasters")
st.markdown("""
This dashboard shows product performance for Afficionado Coffee Roasters.  
It helps identify top-selling products, category contribution, and the relationship between quantity sold and revenue.
""")

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

# Filter data
filtered_df = df[
    (df["product_category"].isin(categories)) &
    (df["product_type"].isin(product_types))
]

# KPI Cards
col1, col2, col3, col4 = st.columns(4)

total_revenue = filtered_df["revenue"].sum()
total_products = filtered_df["product_detail"].nunique()
avg_price = filtered_df["unit_price"].mean()
total_quantity = filtered_df["quantity"].sum()

col1.metric("Total Revenue", f"${total_revenue:,.0f}")
col2.metric("Products", f"{total_products}")
col3.metric("Avg Unit Price", f"${avg_price:.2f}")
col4.metric("Total Quantity Sold", f"{total_quantity:,}")

st.markdown("---")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Products by Revenue")
    top_products = filtered_df.groupby("product_detail")["revenue"].sum().nlargest(15).reset_index()
    fig1 = px.bar(
        top_products,
        x="revenue",
        y="product_detail",
        orientation="h",
        color="revenue",
        color_continuous_scale="Blues",
        height=500
    )
    fig1.update_layout(showlegend=False, yaxis_title="", xaxis_title="Revenue")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Revenue by Category")
    category_rev = filtered_df.groupby("product_category")["revenue"].sum().reset_index()
    fig2 = px.pie(
        category_rev,
        values="revenue",
        names="product_category",
        hole=0.4,
        height=500
    )
    st.plotly_chart(fig2, use_container_width=True)

# Second row
st.subheader("Popularity vs Revenue")

scatter_data = filtered_df.groupby("product_detail").agg({
    "quantity": "sum",
    "revenue": "sum"
}).reset_index()

# Keep top products only
scatter_data = scatter_data.nlargest(50, "revenue")

fig3 = px.scatter(
    scatter_data,
    x="quantity",
    y="revenue",
    size="revenue",
    hover_name="product_detail",
    color="revenue",
    color_continuous_scale="Blues",
    height=550
)

fig3.update_traces(
    textposition="top center",
    textfont_size=1,          # Makes text invisible
    marker=dict(line=dict(width=0.5, color="DarkSlateGrey"))
)

fig3.update_layout(
    xaxis_title="Quantity Sold",
    yaxis_title="Revenue",
    showlegend=False
)

st.plotly_chart(fig3, use_container_width=True)
# Data table
with st.expander("View Filtered Data"):
    st.dataframe(filtered_df, use_container_width=True)