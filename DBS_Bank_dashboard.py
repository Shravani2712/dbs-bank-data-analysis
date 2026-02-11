import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

st.set_page_config(page_title="DBS Bank Executive Dashboard", layout="wide")

# =============================
# FORMAT FUNCTION (K / M / B)
# =============================

def format_number(num):
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.2f}K"
    else:
        return f"{num:.0f}"

# =============================
# LOAD DATA
# =============================

loan_df = pd.read_csv("Loan Data.csv")
credit_df = pd.read_csv("Debit and Credit Data.csv")

credit_df["Transaction_Date"] = pd.to_datetime(credit_df["Transaction_Date"])
credit_df["Month"] = credit_df["Transaction_Date"].dt.month_name()

# =============================
# THEME
# =============================

st.markdown("""
<style>
.kpi-card {
    background: linear-gradient(135deg,#111827,#1f2937);
    padding:20px;
    border-radius:15px;
    text-align:center;
    box-shadow:0px 4px 20px rgba(0,0,0,0.4);
}
.kpi-title {
    font-size:14px;
    color:#9CA3AF;
}
.kpi-value {
    font-size:24px;
    font-weight:bold;
    color:#ffffff;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;color:#A855F7;'>🏦 DBS BANK EXECUTIVE ANALYTICS DASHBOARD</h1>", unsafe_allow_html=True)

dashboard = st.radio(
    "Select Dashboard",
    ["📊 Loan Dashboard", "💳 Credit & Debit Dashboard"],
    horizontal=True
)

# =========================================================
# ================= LOAN DASHBOARD =========================
# =========================================================

if dashboard == "📊 Loan Dashboard":

    df = loan_df.copy()

    st.sidebar.header("Loan Filters")
    state = st.sidebar.multiselect("State", df["State_Name"].dropna().unique())
    grade = st.sidebar.multiselect("Grade", df["Grade"].dropna().unique())
    status = st.sidebar.multiselect("Loan Status", df["Loan_Status"].dropna().unique())

    if state:
        df = df[df["State_Name"].isin(state)]
    if grade:
        df = df[df["Grade"].isin(grade)]
    if status:
        df = df[df["Loan_Status"].isin(status)]

    # ================= KPI =================

    total_loans = df["Loan_Amount"].sum()
    total_funded = df["Funded_Amount"].sum()
    avg_interest = df["Int_Rate"].mean()
    default_rate = (df["Is Default Loan"] == 1).mean() * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Loan Amount</div><div class='kpi-value'>₹ {format_number(total_loans)}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Funded</div><div class='kpi-value'>₹ {format_number(total_funded)}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Interest Rate</div><div class='kpi-value'>{avg_interest:.2f}%</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='kpi-card'><div class='kpi-title'>Default Rate</div><div class='kpi-value'>{default_rate:.2f}%</div></div>", unsafe_allow_html=True)

    st.divider()

    # ================= VISUALS =================

    row1 = st.columns(3)

    with row1[0]:
        fig = px.bar(df.groupby("State_Name")["Loan_Amount"].sum().reset_index(),
                     x="Loan_Amount", y="State_Name",
                     orientation="h",
                     title="Loan Amount by State")
        st.plotly_chart(fig, use_container_width=True)

    with row1[1]:
        fig = px.pie(df, names="Loan_Status", hole=0.5,
                     title="Loan Status Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with row1[2]:
        fig = px.bar(df.groupby("Purpose_Category")["Loan_Amount"].sum().reset_index(),
                     x="Purpose_Category", y="Loan_Amount",
                     title="Loan by Purpose")
        st.plotly_chart(fig, use_container_width=True)

    row2 = st.columns(3)

    with row2[0]:
        fig = px.histogram(df, x="Credit_Score",
                           nbins=30,
                           title="Credit Score Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with row2[1]:
        fig = px.box(df, x="Grade", y="Loan_Amount",
                     title="Loan Amount by Grade")
        st.plotly_chart(fig, use_container_width=True)

    with row2[2]:
        fig = px.scatter(df, x="Int_Rate", y="Loan_Amount",
                         color="Loan_Status",
                         title="Interest Rate vs Loan Amount")
        st.plotly_chart(fig, use_container_width=True)

    if st.checkbox("View Loan Dataset"):
        st.dataframe(df)

# =========================================================
# ================= CREDIT DASHBOARD =======================
# =========================================================

else:

    df = credit_df.copy()

    st.sidebar.header("Transaction Filters")
    bank = st.sidebar.multiselect("Bank", df["Bank Name"].unique())
    txn_type = st.sidebar.multiselect("Transaction Type", df["Transaction_Type"].unique())
    method = st.sidebar.multiselect("Transaction Method", df["Transaction_Method"].unique())

    if bank:
        df = df[df["Bank Name"].isin(bank)]
    if txn_type:
        df = df[df["Transaction_Type"].isin(txn_type)]
    if method:
        df = df[df["Transaction_Method"].isin(method)]

    # ================= KPI =================

    total_txn = df["Amount"].sum()
    avg_balance = df["Balance"].mean()
    total_customers = df["Customer_ID"].nunique()
    debit_ratio = (df["Transaction_Type"] == "Debit").mean() * 100

    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Transactions</div><div class='kpi-value'>₹ {format_number(total_txn)}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='kpi-card'><div class='kpi-title'>Avg Balance</div><div class='kpi-value'>₹ {format_number(avg_balance)}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='kpi-card'><div class='kpi-title'>Total Customers</div><div class='kpi-value'>{format_number(total_customers)}</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='kpi-card'><div class='kpi-title'>Debit %</div><div class='kpi-value'>{debit_ratio:.2f}%</div></div>", unsafe_allow_html=True)

    st.divider()

    row1 = st.columns(3)

    with row1[0]:
        fig = px.line(df.groupby("Month")["Amount"].sum().reset_index(),
                      x="Month", y="Amount",
                      markers=True,
                      title="Monthly Transaction Trend")
        st.plotly_chart(fig, use_container_width=True)

    with row1[1]:
        fig = px.pie(df, names="Transaction_Type", values="Amount",
                     hole=0.5,
                     title="Transaction Type Distribution")
        st.plotly_chart(fig, use_container_width=True)

    with row1[2]:
        fig = px.bar(df.groupby("Branch")["Amount"].sum().reset_index(),
                     x="Amount", y="Branch",
                     orientation="h",
                     title="Transaction by Branch")
        st.plotly_chart(fig, use_container_width=True)

    row2 = st.columns(3)

    with row2[0]:
        fig = px.treemap(df.groupby("Bank Name")["Amount"].sum().reset_index(),
                         path=["Bank Name"],
                         values="Amount",
                         title="Bank Wise Transaction")
        st.plotly_chart(fig, use_container_width=True)

    with row2[1]:
        fig = px.box(df, x="Transaction_Method", y="Amount",
                     title="Transaction Amount by Method")
        st.plotly_chart(fig, use_container_width=True)

    with row2[2]:
        top10 = df.groupby("Customer_Name")["Amount"].sum().nlargest(10).reset_index()
        fig = px.bar(top10,
                     x="Amount", y="Customer_Name",
                     orientation="h",
                     title="Top 10 Customers")
        st.plotly_chart(fig, use_container_width=True)

    if st.checkbox("View Transaction Dataset"):
        st.dataframe(df)