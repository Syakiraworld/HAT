import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================================
# AUTH
# =====================================================
if "login" not in st.session_state or not st.session_state.login:
    st.warning("Silakan login terlebih dahulu")
    st.stop()

st.set_page_config(page_title="HAT – Tracking", layout="wide")

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.image("assets/logo.png", use_container_width=True)
st.sidebar.markdown("### 📊 Navigasi")

if st.sidebar.button("🚪 Logout"):
    st.session_state.clear()
    st.switch_page("app.py")

# =====================================================
# DATA SOURCE
# =====================================================
SPREADSHEET_ID = "1-o9ZqiD9AKtkwhgvK5x-cwDTjdfGn4hOSBmLOEz4dII"
SHEET_GID = "513906626"

CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
)

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    df["CUSTOMER NO"] = df["CUSTOMER NO"].astype(str)
    df["ORDER STAR NO"] = df["ORDER STAR NO"].astype(str)
    df["ORDER NO"] = df["ORDER NO"].astype(str)
    
    return df

df = load_data()

# =====================================================
# STATUS LOGIC
# =====================================================
def get_status(row):
    order_no = row["ORDER NO"]
    etd = row["ETD AHM"]

    if pd.isna(etd) or etd == "":
        if order_no.startswith("235"):
            return "🟢 Delivered"
        if order_no.startswith("125"):
            return "🔴 PO AHM"
    else:
        if order_no.startswith("125"):
            return "🟡 Intransit"
    return "-"

df["Keterangan"] = df.apply(get_status, axis=1)

# =====================================================
# FILTER BY ROLE
# =====================================================
if st.session_state.role == "ADMIN":
    st.sidebar.markdown("### 🔎 Pilih AHASS")
    ahass_list = sorted(df["CUSTOMER NO"].unique())
    selected_ahass = st.sidebar.selectbox(
        "AHASS", ["ALL AHASS"] + ahass_list
    )

    if selected_ahass != "ALL AHASS":
        df = df[df["CUSTOMER NO"] == selected_ahass]

else:
    cust_no = st.session_state.customer_no
    df = df[df["CUSTOMER NO"] == cust_no]
    st.sidebar.info(f"🔒 AHASS: {cust_no}")

# =====================================================
# HEADER
# =====================================================
st.title("📦 Fitur 1 – Tracking Online Hotline")
st.caption(
    f"📅 Data terakhir update: "
    f"{datetime.now().strftime('%d/%m/%Y %H:%M')}"
)

# =====================================================
# FILTER PO
# =====================================================
po_list = sorted(df["ORDER STAR NO"].unique())
selected_po = st.selectbox("Nomor PO", ["ALL PO"] + po_list)

if selected_po != "ALL PO":
    df = df[df["ORDER STAR NO"] == selected_po]

# =====================================================
# KPI
# =====================================================
c1, c2, c3 = st.columns(3)
c1.metric("Total PO", df["ORDER STAR NO"].nunique())
c2.metric("Delivered", df[df["Keterangan"].str.contains("Delivered")]["ORDER STAR NO"].nunique())
c3.metric("Intransit", df[df["Keterangan"].str.contains("Intransit")]["ORDER STAR NO"].nunique())

# =====================================================
# TABLE
# =====================================================
st.subheader("📋 Tabel Tracking")

exclude = ["ORDER DATE", "ORDER STAR DATE", "PO NO", "PO dan ETD"]
final_cols = [c for c in df.columns if c not in exclude]

st.dataframe(df[final_cols], use_container_width=True)
