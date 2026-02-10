import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DBS Bank Data Analysis",
    layout="wide"
)

st.title("🏦 DBS Bank Unified Dashboard")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    loan_df = pd.read_excel("Loan Dataset.xlsx")
    cd_df = pd.read_excel("Debit and Credit Dataset.xlsx")

    # Convert Date columns to datetime
    loan_df["Date"] = pd.to_datetime(loan_df["Date"])
    cd_df["Date"] = pd.to_datetime(cd_df["Date"])

    return loan_df, cd_df

loan_df, cd_df = load_data()

# ---------------- TABS ----------------
tab1, tab2 = st.tabs(["💰 Loan Dashboard", "💳 Credit & Debit Dashboard"])

# =====================================================
# ================= LOAN DASHBOARD ====================
# =====================================================
with tab1:
    st.subheader("Loan Analysis")

    # ---------- Filters ----------
    st.sidebar.header("Loan Filters")

    customer = st.sidebar.multiselect(
        "Select Customer",
        options=loan_df["Customer_ID"].unique(),
        default=loan_df["Customer_ID"].unique()
    )

    loan_type = st.sidebar.multiselect(
        "Select Loan Type",
        options=loan_df["Loan_Type"].unique(),
        default=loan_df["Loan_Type"].unique()
    )

    date_range = st.sidebar.date_input(
        "Select Date Range",
        [loan_df["Date"].min(), loan_df["Date"].max()]
    )

    # ---------- Apply Filters ----------
    filtered_loan = loan_df[
        (loan_df["Customer_ID"].isin(customer)) &
        (loan_df["Loan_Type"].isin(loan_type)) &
        (loan_df["Date"] >= pd.to_datetime(date_range[0])) &
        (loan_df["Date"] <= pd.to_datetime(date_range[1]))
    ]

    # ---------- KPIs ----------
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Loan Amount", f"₹ {filtered_loan['Loan_Amount'].sum():,.0f}")
    col2.metric("Average Loan", f"₹ {filtered_loan['Loan_Amount'].mean():,.0f}")
    col3.metric("Total Customers", filtered_loan["Customer_ID"].nunique())

    # ---------- Charts ----------
    col4, col5 = st.columns(2)

    with col4:
        fig1 = px.bar(
            filtered_loan,
            x="Loan_Type",
            y="Loan_Amount",
            color="Loan_Status",
            title="Loan Amount by Loan Type"
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col5:
        fig2 = px.pie(
            filtered_loan,
            names="Loan_Status",
            title="Loan Status Distribution"
        )
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Loan Records")
    st.dataframe(filtered_loan)

# =====================================================
# ============== CREDIT & DEBIT DASHBOARD ==============
# =====================================================
with tab2:
    st.subheader("Credit & Debit Analysis")

    # ---------- Filters ----------
    st.sidebar.header("Credit & Debit Filters")

    cust_cd = st.sidebar.multiselect(
        "Select Customer",
        options=cd_df["Customer_ID"].unique(),
        default=cd_df["Customer_ID"].unique()
    )

    date_range_cd = st.sidebar.date_input(
        "Select Transaction Date Range",
        [cd_df["Date"].min(), cd_df["Date"].max()],
        key="cd_date"
    )

    filtered_cd = cd_df[
        (cd_df["Customer_ID"].isin(cust_cd)) &
        (cd_df["Date"] >= pd.to_datetime(date_range_cd[0])) &
        (cd_df["Date"] <= pd.to_datetime(date_range_cd[1]))
    ]

    # ---------- KPIs ----------
    col6, col7, col8 = st.columns(3)

    col6.metric("Total Credit", f"₹ {filtered_cd['Credit_Amount'].sum():,.0f}")
    col7.metric("Total Debit", f"₹ {filtered_cd['Debit_Amount'].sum():,.0f}")
    col8.metric("Net Balance", f"₹ {(filtered_cd['Credit_Amount'].sum() - filtered_cd['Debit_Amount'].sum()):,.0f}")

    # ---------- Charts ----------
    col9, col10 = st.columns(2)

    with col9:
        fig3 = px.line(
            filtered_cd,
            x="Date",
            y="Credit_Amount",
            title="Credit Trend"
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col10:
        fig4 = px.line(
            filtered_cd,
            x="Date",
            y="Debit_Amount",
            title="Debit Trend"
        )
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Transaction Records")
    st.dataframe(filtered_cd)