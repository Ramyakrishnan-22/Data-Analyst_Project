import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit.components.v1 as components
DB_CONNECTION_STRING = "postgresql://postgres:ramya2201@localhost:5432/ola_data"
engine = create_engine(DB_CONNECTION_STRING)

st.set_page_config(page_title="🚖 Ola Dashboard", layout="wide")
st.title("🚖 Ola Rides Analysis Dashboard")
# 📂 CSV Upload
uploaded_file = st.file_uploader("📤 Upload OLA_DataSet.csv", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    # Convert all columns to lowercase
    df.columns = [col.lower() for col in df.columns]
    df.to_sql("ola", engine, if_exists="replace", index=False)
    st.success("✅ CSV data uploaded to PostgreSQL!")
    st.dataframe(df.head())
# 📊 SQL Queries
st.header("🔍 Run Ola Queries")

queries = {
    "View first 10 rows": "SELECT * FROM ola LIMIT 10;",
    "Count total bookings": "SELECT COUNT(*) AS total_bookings FROM ola;",
    "Distinct vehicle types": "SELECT DISTINCT vehicle_type FROM ola;",
    "Average ride distance": "SELECT ROUND(AVG(ride_distance),2) AS avg_ride_distance_km FROM ola;",
    "Longest and shortest rides": """
        SELECT MAX(ride_distance) AS longest_ride_km,
               MIN(ride_distance) AS shortest_ride_km
        FROM ola;
    """,
    "Average distance per vehicle type": """
        SELECT vehicle_type, ROUND(AVG(ride_distance),2) AS avg_distance_km
        FROM ola
        GROUP BY vehicle_type
        ORDER BY avg_distance_km DESC;
    """,
    "Total revenue": "SELECT SUM(booking_value) AS total_revenue FROM ola;",
    "Average booking value": "SELECT ROUND(AVG(booking_value),2) AS avg_booking_value FROM ola;",
    "Revenue by payment method": """
        SELECT payment_method, SUM(booking_value) AS total_revenue
        FROM ola
        GROUP BY payment_method
        ORDER BY total_revenue DESC;
    """,
    "Revenue per vehicle type": """
        SELECT vehicle_type, SUM(booking_value) AS total_revenue
        FROM ola
        GROUP BY vehicle_type
        ORDER BY total_revenue DESC;
    """,
    "Average driver & customer ratings": """
        SELECT ROUND(AVG(driver_ratings),2) AS avg_driver_rating,
               ROUND(AVG(customer_rating),2) AS avg_customer_rating
        FROM ola;
    """,
    "Vehicle type with highest avg driver rating": """
        SELECT vehicle_type, ROUND(AVG(driver_ratings),2) AS avg_driver_rating
        FROM ola
        GROUP BY vehicle_type
        ORDER BY avg_driver_rating DESC;
    """,
    "Distribution of customer ratings": """
        SELECT customer_rating, COUNT(*) AS total_rides
        FROM ola
        GROUP BY customer_rating
        ORDER BY customer_rating;
    """,
    "Total canceled rides by customers": """
        SELECT COUNT(canceled_rides_by_customer) AS total_customer_cancellations
        FROM ola;
    """,
    "Most common driver cancellation reasons": """
        SELECT canceled_rides_by_driver, COUNT(*) AS total_cases
        FROM ola
        WHERE canceled_rides_by_driver IS NOT NULL
        GROUP BY canceled_rides_by_driver
        ORDER BY total_cases DESC;
    """,
    "Count incomplete rides and reasons": """
        SELECT incomplete_rides_reason, COUNT(*) AS total_incomplete
        FROM ola
        WHERE incomplete_rides_reason IS NOT NULL
        GROUP BY incomplete_rides_reason
        ORDER BY total_incomplete DESC;
    """,
    "Bookings per day": """
        SELECT date, COUNT(*) AS total_bookings
        FROM ola
        GROUP BY date
        ORDER BY date;
    """,
    "Average booking value by day": """
        SELECT date, ROUND(AVG(booking_value),2) AS avg_value
        FROM ola
        GROUP BY date
        ORDER BY date;
    """,
    "Peak booking hours": """
        SELECT EXTRACT(HOUR FROM time) AS hour, COUNT(*) AS total_bookings
        FROM ola
        GROUP BY hour
        ORDER BY total_bookings DESC;
    """,
    "Average vehicle turnaround time": """
        SELECT ROUND(AVG(EXTRACT(EPOCH FROM v_tat)/60),2) AS avg_vehicle_tat_minutes
        FROM ola;
    """,
    "Average customer turnaround time": """
        SELECT ROUND(AVG(EXTRACT(EPOCH FROM c_tat)/60),2) AS avg_customer_tat_minutes
        FROM ola;
    """,
    "Compare TAT per vehicle type": """
        SELECT vehicle_type,
               ROUND(AVG(EXTRACT(EPOCH FROM v_tat)/60),2) AS avg_v_tat_mins,
               ROUND(AVG(EXTRACT(EPOCH FROM c_tat)/60),2) AS avg_c_tat_mins
        FROM ola
        GROUP BY vehicle_type;
    """,
    "Top 5 vehicle types by avg revenue per ride": """
        SELECT vehicle_type,
               ROUND(AVG(booking_value),2) AS avg_revenue_per_ride,
               ROUND(AVG(ride_distance),2) AS avg_distance
        FROM ola
        GROUP BY vehicle_type
        ORDER BY avg_revenue_per_ride DESC
        LIMIT 5;
    """,
    "Correlation between ride distance and booking value": """
        SELECT ROUND(CORR(ride_distance, booking_value)::NUMERIC,2) AS distance_value_correlation
        FROM ola;
    """,
    "Total bookings count": "SELECT COUNT(booking_id) AS total_booking FROM ola;"
}

selected_query = st.selectbox("🧠 Choose a query:", list(queries.keys()))

if st.button("Run Query"):
    try:
        with engine.connect() as conn:
            df_result = pd.read_sql(text(queries[selected_query]), conn)
        st.dataframe(df_result)
    except Exception as e:
        st.error(f"Error executing query: {e}")

# Bar chart for revenue per vehicle type
if st.checkbox("📊 Show revenue per vehicle type chart"):
    chart_query = """
        SELECT vehicle_type, SUM(booking_value) AS total_revenue
        FROM ola
        GROUP BY vehicle_type
        ORDER BY total_revenue DESC;
    """
    chart_df = pd.read_sql(text(chart_query), engine)
    st.bar_chart(chart_df.set_index("vehicle_type"))
# Embed Power BI Report (optional)
st.header("📊 Power BI Report Embed")
powerbi_embed_url = "https://app.powerbi.com/reportEmbed?reportId=a3787665-0d33-4e17-9f56-e9b7fd58343b&autoAuth=true&ctid=5504dd51-3097-475e-80a0-36b5fbe79b94"
components.html(f"""
<iframe width="100%" height="600" src="{powerbi_embed_url}" frameborder="0" allowFullScreen="true"></iframe>
""", height=650)
