
import streamlit as st
import pandas as pd
import numpy as np

st.title("Sales Analysis Dashboard ")

st.write("Upload CSV file and analyze your sales data")

# upload csv
file = st.file_uploader("Upload CSV", type=["csv"])

if file is not None:

    df = pd.read_csv(file)

    st.success("File uploaded successfully")

    # check required columns
    required = ["product", "city", "qty", "price"]

    if all(col in df.columns for col in required):

        # total sales
        df["total_sales"] = df["qty"] * df["price"]

        # sidebar filters
        st.sidebar.header("Filters")

        city = st.sidebar.multiselect(
            "Select City",
            df["city"].unique(),
            default=df["city"].unique()
        )

        product = st.sidebar.multiselect(
            "Select Product",
            df["product"].unique(),
            default=df["product"].unique()
        )

        # filter data
        filtered = df[
            (df["city"].isin(city)) &
            (df["product"].isin(product))
        ]

        # stats
        total_sales = filtered["total_sales"].sum()
        avg_sales = np.mean(filtered["total_sales"])

        if not filtered.empty:
            best_product = filtered.groupby("product")[
                "total_sales"
            ].sum().idxmax()
        else:
            best_product = "No Data"

        st.subheader("Quick Stats")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Sales", total_sales)
        col2.metric("Average Sales", round(avg_sales, 2))
        col3.metric("Best Product", best_product)

        # chart
        st.subheader("City Wise Sales")

        city_sales = filtered.groupby("city")[
            "total_sales"
        ].sum()

        st.bar_chart(city_sales)

        # data table
        st.subheader("Filtered Data")
        st.dataframe(filtered)

    else:
        st.error(
            "CSV must contain: product, city, qty, price"
        )

else:
    st.info("Please upload CSV file")