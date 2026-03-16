import streamlit as st
import pandas as pd
from email_notifier import send_email

st.set_page_config(page_title="NEPSE Live Market Dashboard", layout="wide")

st.title("NEPSE Live Market Dashboard")


# AUTO PAGE REFRESH EVERY 60 SEC
st.markdown(
    """
    <script>
        setTimeout(function(){
            window.location.reload();
        }, 60000);
    </script>
    """,
    unsafe_allow_html=True
)


# LOAD LIVE DATA
@st.cache_data(ttl=60)
def load_live_data():
    url = "https://www.merolagani.com/LatestMarket.aspx"
    tables = pd.read_html(url)
    df = tables[0]

    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    return df


try:
    df = load_live_data()
    st.success("Live market data loaded successfully")
except:
    st.error("Failed to fetch live data")
    st.stop()


# CLEAN PRICE DATA
df["LTP"] = pd.to_numeric(
    df["LTP"].astype(str).str.replace(",", ""),
    errors="coerce"
)

if "Previous Close" in df.columns:
    df["Previous Close"] = pd.to_numeric(
        df["Previous Close"].astype(str).str.replace(",", ""),
        errors="coerce"
    )
    df["LTP"] = df["LTP"].fillna(df["Previous Close"])


# MARKET SUMMARY
st.subheader("Market Summary")

total_stocks = len(df)
highest_price = df["LTP"].max()
lowest_price = df["LTP"].min()

col1, col2, col3 = st.columns(3)

col1.metric("Stocks Listed", total_stocks)
col2.metric("Highest Price", round(highest_price, 2))
col3.metric("Lowest Price", round(lowest_price, 2))

st.divider()


# SEARCH STOCK
st.header("Search Stock")

search = st.text_input("Enter Stock Symbol (Example: NABIL)").upper()

if search:

    result = df[df["Symbol"].str.upper() == search]

    if not result.empty:
        st.success("Stock Found")
        st.dataframe(result, width="stretch")
    else:
        st.error("Stock Not Found")


st.divider()


# EMAIL ALERT SECTION
st.header("Email Stock Alert")

email = st.text_input("Enter your email for price alerts")
target_price = st.number_input("Enter target price", min_value=0.0, step=1.0)


# STORE MULTIPLE ALERTS
if "alerts" not in st.session_state:
    st.session_state.alerts = []


# ADD ALERT
if st.button("Set Price Alert"):

    if email and search and target_price > 0:

        alert = {
            "email": email,
            "stock": search,
            "target": target_price
        }

        st.session_state.alerts.append(alert)

        st.success(f"Alert added for {search} at price {target_price}")

    else:
        st.warning("Please enter stock symbol, email and target price")


# CHECK ALERTS
for alert in st.session_state.alerts:

    alert_stock = alert["stock"]
    alert_email = alert["email"]
    alert_target = alert["target"]

    result = df[df["Symbol"].str.upper() == alert_stock]

    if not result.empty:

        current_price = result["LTP"].values[0]

        if current_price >= alert_target:

            send_email(alert_email, alert_stock, current_price)

            st.success(f"Target reached! Email sent for {alert_stock}")

            st.session_state.alerts.remove(alert)


# SHOW ACTIVE ALERTS
st.subheader("Active Alerts")

if st.session_state.alerts:

    alerts_df = pd.DataFrame(st.session_state.alerts)

    st.dataframe(alerts_df, width="stretch")

else:

    st.write("No active alerts")


st.divider()


# FULL MARKET OVERVIEW
st.header("Full Market Overview")

st.dataframe(df, width="stretch")