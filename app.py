import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"
)

# minimal dark tweak — just background, no fake HTML
st.markdown("""
<style>
.stApp { background-color: #0d1117; color: #e6edf3; }
[data-testid="stSidebar"] { background-color: #161b22; }
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# sidebar
st.sidebar.title("📊 Sales Dashboard")
st.sidebar.divider()
file = st.sidebar.file_uploader("Upload your CSV", type=["csv"])

if file is None:
    st.title("📊 Sales Dashboard")
    st.info("Upload your CSV file from the sidebar to get started.")
    st.stop()

df = pd.read_csv(file)
required = ["product", "city", "qty", "price"]
if not all(c in df.columns for c in required):
    st.error(f"CSV must have these columns: {', '.join(required)}")
    st.stop()

df["total_sales"] = df["qty"] * df["price"]

has_date     = "date" in df.columns
has_category = "category" in df.columns
has_status   = "status" in df.columns

if has_date:
    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M").astype(str)

# filters
st.sidebar.divider()
st.sidebar.subheader("Filters")

cities = st.sidebar.multiselect(
    "City", sorted(df["city"].unique()), default=sorted(df["city"].unique())
)
products = st.sidebar.multiselect(
    "Product", sorted(df["product"].unique()), default=sorted(df["product"].unique())
)
if has_category:
    categories = st.sidebar.multiselect(
        "Category", sorted(df["category"].unique()), default=sorted(df["category"].unique())
    )

filtered = df[df["city"].isin(cities) & df["product"].isin(products)]
if has_category:
    filtered = filtered[filtered["category"].isin(categories)]

if filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# header
st.title("📊 Sales Dashboard")
st.caption(f"Showing {len(filtered):,} of {len(df):,} records")
st.divider()

# KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue",   f"Rs {filtered['total_sales'].sum():,.0f}")
k2.metric("Total Orders",    f"{len(filtered):,}")
k3.metric("Avg Order Value", f"Rs {filtered['total_sales'].mean():,.0f}")
k4.metric("Best Product",    filtered.groupby("product")["total_sales"].sum().idxmax())
k5.metric("Top City",        filtered.groupby("city")["total_sales"].sum().idxmax())

st.divider()

# charts row 1
c1, c2 = st.columns([3, 2])

with c1:
    st.subheader("City Wise Revenue")
    city_df = (
        filtered.groupby("city")["total_sales"]
        .sum().sort_values(ascending=False).reset_index()
    )
    fig = px.bar(
        city_df, x="city", y="total_sales",
        color="total_sales", color_continuous_scale="Blues",
        labels={"total_sales": "Revenue (Rs)", "city": "City"},
        template="plotly_dark"
    )
    fig.update_coloraxes(showscale=False)
    fig.update_layout(plot_bgcolor="#161b22", paper_bgcolor="#161b22")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Product Revenue Share")
    prod_df = filtered.groupby("product")["total_sales"].sum().reset_index()
    fig2 = px.pie(
        prod_df, names="product", values="total_sales",
        hole=0.4, template="plotly_dark",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig2.update_layout(paper_bgcolor="#161b22")
    st.plotly_chart(fig2, use_container_width=True)

# charts row 2
c3, c4 = st.columns([3, 2])

with c3:
    if has_date:
        st.subheader("Monthly Sales Trend")
        monthly = filtered.groupby("month")["total_sales"].sum().reset_index()
        fig3 = px.line(
            monthly, x="month", y="total_sales",
            markers=True, template="plotly_dark",
            color_discrete_sequence=["#79c0ff"],
            labels={"total_sales": "Revenue (Rs)", "month": "Month"}
        )
        fig3.update_traces(line_width=3, marker_size=8)
        fig3.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.subheader("Qty Sold by Product")
        qty_df = filtered.groupby("product")["qty"].sum().sort_values(ascending=False).reset_index()
        fig3 = px.bar(
            qty_df, x="product", y="qty",
            template="plotly_dark",
            color_discrete_sequence=["#79c0ff"],
            labels={"qty": "Qty Sold", "product": "Product"}
        )
        fig3.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22")
        st.plotly_chart(fig3, use_container_width=True)

with c4:
    st.subheader("Top 5 Products")
    top5 = (
        filtered.groupby("product")["total_sales"]
        .sum().nlargest(5).reset_index()
    )
    fig4 = px.bar(
        top5, x="total_sales", y="product",
        orientation="h", template="plotly_dark",
        color="total_sales", color_continuous_scale="Reds",
        labels={"total_sales": "Revenue (Rs)", "product": ""}
    )
    fig4.update_coloraxes(showscale=False)
    fig4.update_layout(
        yaxis=dict(autorange="reversed"),
        paper_bgcolor="#161b22", plot_bgcolor="#161b22"
    )
    st.plotly_chart(fig4, use_container_width=True)

# status chart
if has_status:
    st.divider()
    st.subheader("Order Status Breakdown")
    status_df = filtered["status"].value_counts().reset_index()
    status_df.columns = ["status", "count"]
    fig5 = px.bar(
        status_df, x="status", y="count",
        color="status", template="plotly_dark",
        color_discrete_map={
            "Completed": "#3fb950",
            "Pending":   "#ffa657",
            "Cancelled": "#ff7b72"
        },
        labels={"count": "Orders", "status": "Status"}
    )
    fig5.update_layout(paper_bgcolor="#161b22", plot_bgcolor="#161b22", showlegend=False)
    st.plotly_chart(fig5, use_container_width=True)

# data table
st.divider()
st.subheader("Data Table")

col_dl, _ = st.columns([1, 4])
with col_dl:
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="filtered_sales.csv",
        mime="text/csv",
        use_container_width=True
    )

st.dataframe(filtered.reset_index(drop=True), use_container_width=True, height=300)
