"""
Simple dashboard. Run with:  streamlit run dashboard.py
"""
import pandas as pd
import streamlit as st

from database import get_products, get_price_history, get_recent_alerts

st.set_page_config(page_title="Price Tracker", layout="wide")
st.title("Price Tracker Dashboard")

products = get_products()
alerts = get_recent_alerts()

col1, col2 = st.columns(2)
col1.metric("Products tracked", len(products))
col2.metric("Price drop alerts", len(alerts))

st.subheader("Price history")
if products:
    names = {p["product_name"]: p["product_url"] for p in products}
    choice = st.selectbox("Choose a product", list(names))
    history = pd.DataFrame(get_price_history(names[choice]))
    if len(history) > 1:
        history["scraped_at"] = pd.to_datetime(history["scraped_at"])
        st.line_chart(history.set_index("scraped_at")["price"])
    st.dataframe(history, use_container_width=True)
else:
    st.info("No data yet. Run main.py first.")

st.subheader("Recent price drop alerts")
st.dataframe(pd.DataFrame(alerts), use_container_width=True) if alerts else st.info("No alerts yet.")
