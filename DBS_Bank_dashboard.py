import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="DBS Bank Analytics v3.0", layout="wide")

# --- 1. DATA GENERATION (SIMULATED FOR ALL CHART TYPES) ---
@st.cache_data
def load_all_data():
    # Loan Data
    loan_df = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] * 6,
        'State': ['Punjab', 'Assam', 'Bihar', 'Rajasthan', 'Haryana', 'Odisha'] * 6,
        'Product': ['JLG30K', 'JLG35K', 'JLG46K', 'JLG44K', 'JLG30K', 'JLG35K'] * 6,
        'Amount': [45, 32, 18, 55, 40, 22, 50, 38, 25, 60, 42, 28, 48, 35, 20, 58, 45, 30, 52, 40, 22, 65, 48, 35, 55, 42, 25, 70, 50, 38, 58, 45, 28, 75, 52, 40],
        'Clients': [120, 90, 45, 150, 110, 65] * 6,
        'Performance': ['High', 'Medium', 'Low', 'High', 'Medium', 'Low'] * 6,
        'Religion': ['Hindu', 'Sikh', 'Muslim', 'Christian'] * 9
    })
    
    # Transaction Data
    trans_df = pd.DataFrame({
        'Bank': ['Axis Bank', 'HDFC Bank', 'ICICI Bank', 'Kotak Bank', 'SBI', 'PNB'],
        'Branch': ['Main Branch', 'City Center', 'North Branch', 'East Branch', 'Downtown', 'Suburban'],
        'Credit_Amt': [120, 130, 115, 110, 140, 125],
        'Debit_Amt': [118, 125, 112, 108, 135, 120],
        'Risk': ['Normal', 'Normal', 'High Risk', 'Normal', 'High Risk', 'Normal'],
        'Growth': [0.45, 0.38, 0.30, 0.32, 0.28, 0.25]
    })
    return loan_df, trans_df

df_l_raw, df_t_raw = load_all_data()

# --- 2. NAVIGATION ---
if 'page' not in st.session_state:
    st.session_state.page = 'Loan'

st.markdown("<h1 style='text-align: center; color: #E31837;'>🏦 DBS BANK CONSOLIDATED ANALYTICS</h1>", unsafe_allow_html=True)
n1, n2 = st.columns(2)
with n1:
    if st.button("💰 LOAN PORTFOLIO", use_container_width=True): st.session_state.page = 'Loan'
with n2:
    if st.button("💳 TRANSACTION & RISK", use_container_width=True): st.session_state.page = 'Trans'

st.divider()

# --- 3. LOAN DASHBOARD ---
if st.session_state.page == 'Loan':
    # Filters
    st.sidebar.header("Loan View Filters")
    f_state = st.sidebar.multiselect("State Name", df_l_raw['State'].unique(), default=[])
    f_prod = st.sidebar.multiselect("Product ID", df_l_raw['Product'].unique(), default=[])
    
    # Filter Logic
    df_l = df_l_raw.copy()
    if f_state: df_l = df_l[df_l['State'].isin(f_state)]
    if f_prod: df_l = df_l[df_l['Product'].isin(f_prod)]

    # Dynamic KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Clients", f"{df_l['Clients'].sum():,}")
    k2.metric("Total Loan Amt", f"₹{df_l['Amount'].sum()}M")
    k3.metric("Avg Loan Size", f"₹{df_l['Amount'].mean():.1f}K")
    k4.metric("Active States", df_l['State'].nunique())

    # Visual Row 1: Area & Column
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.write("### 📈 Disbursement Trend (Area Chart)")
        st.plotly_chart(px.area(df_l, x='Month', y='Amount', color='State', template="plotly_white"), use_container_width=True)
    with r1c2:
        st.write("### 📊 Client Count by Religion (Column Chart)")
        st.plotly_chart(px.bar(df_l, x='Religion', y='Clients', color='Religion', text_auto=True), use_container_width=True)

    # Visual Row 2: Treemap & Pie
    r2c1, r2c2 = st.columns([1.5, 1])
    with r2c1:
        st.write("### 🌳 State & Product Hierarchy (Treemap)")
        st.plotly_chart(px.treemap(df_l, path=['State', 'Product'], values='Amount', color='Amount'), use_container_width=True)
    with r2c2:
        st.write("### 🍕 Performance Split (Donut Chart)")
        st.plotly_chart(px.pie(df_l, values='Amount', names='Performance', hole=0.5), use_container_width=True)

    with st.expander("📁 View Loan Dataset"):
        st.dataframe(df_l, use_container_width=True)

# --- 4. TRANSACTION DASHBOARD ---
else:
    # Filters
    st.sidebar.header("Transaction View Filters")
    f_bank = st.sidebar.multiselect("Select Bank", df_t_raw['Bank'].unique(), default=[])
    f_risk = st.sidebar.multiselect("Risk Level", df_t_raw['Risk'].unique(), default=[])

    # Filter Logic
    df_t = df_t_raw.copy()
    if f_bank: df_t = df_t[df_t['Bank'].isin(f_bank)]
    if f_risk: df_t = df_t[df_t['Risk'].isin(f_risk)]

    # Dynamic KPIs
    tk1, tk2, tk3, tk4 = st.columns(4)
    tk1.metric("Total Credit", f"₹{df_t['Credit_Amt'].sum():.1f}M")
    tk2.metric("Total Debit", f"₹{df_t['Debit_Amt'].sum():.1f}M")
    tk3.metric("Avg Growth", f"{df_t['Growth'].mean()*100:.1f}%")
    tk4.metric("Risk Alerts", len(df_t[df_t['Risk'] == 'High Risk']))

    # Visual Row 1: Line & Funnel
    tr1c1, tr1c2 = st.columns(2)
    with tr1c1:
        st.write("### 📉 Growth Rate by Bank (Line Chart)")
        st.plotly_chart(px.line(df_t, x='Bank', y='Growth', markers=True, template="plotly_dark"), use_container_width=True)
    with tr1c2:
        st.write("### 🌪️ Transaction Volume (Funnel Chart)")
        st.plotly_chart(px.funnel(df_t.sort_values('Credit_Amt'), x='Credit_Amt', y='Bank'), use_container_width=True)

    # Visual Row 2: Horizontal Bar & Multi-Metric
    tr2c1, tr2c2 = st.columns(2)
    with tr2c1:
        st.write("### 📊 Credit vs Debit (Side-by-Side Bar)")
        fig_dual = go.Figure(data=[
            go.Bar(name='Credit', x=df_t['Bank'], y=df_t['Credit_Amt']),
            go.Bar(name='Debit', x=df_t['Bank'], y=df_t['Debit_Amt'])
        ])
        st.plotly_chart(fig_dual, use_container_width=True)
    with tr2c2:
        st.write("### 🎯 Risk Distribution (Sunburst)")
        st.plotly_chart(px.sunburst(df_t, path=['Risk', 'Bank'], values='Credit_Amt', color='Risk',
                                   color_discrete_map={'Normal':'green', 'High Risk':'red'}), use_container_width=True)

    with st.expander("📁 View Transaction Dataset"):
        st.dataframe(df_t, use_container_width=True)