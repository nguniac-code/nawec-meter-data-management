
import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(
    page_title="NAWEC Meter Data Management",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ NAWEC Meter Data Management System")
st.write("Manage customer and electricity meter records.")

# Connect to SQLite database
conn = sqlite3.connect("nawec.db")
cursor = conn.cursor()

# Create database table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS meters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT,
        meter_number TEXT UNIQUE,
        location TEXT,
        meter_reading REAL
    )
""")
conn.commit()

# Navigation
menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Add Meter", "View Records"]
)

if menu == "Dashboard":
    st.subheader("Dashboard")

    df = pd.read_sql_query(
        "SELECT * FROM meters", conn
    )

    col1, col2 = st.columns(2)
    col1.metric("Total Meters", len(df))
    col2.metric(
        "Total Meter Readings",
        f"{df['meter_reading'].sum():,.2f}"
    )

    st.dataframe(df, use_container_width=True)

elif menu == "Add Meter":
    st.subheader("Register a Meter")

    with st.form("meter_form"):
        name = st.text_input("Customer Name")
        number = st.text_input("Meter Number")
        location = st.text_input("Location")
        reading = st.number_input(
            "Meter Reading",
            min_value=0.0,
            step=1.0
        )

        submit = st.form_submit_button("Save Meter")

        if submit:
            if not name.strip() or not number.strip():
                st.error("Enter the customer name and meter number.")
            else:
                try:
                    cursor.execute("""
                        INSERT INTO meters
                        (customer_name, meter_number, location, meter_reading)
                        VALUES (?, ?, ?, ?)
                    """, (name, number, location, reading))
                    conn.commit()
                    st.success("Meter registered successfully!")
                except sqlite3.IntegrityError:
                    st.error("This meter number already exists.")

elif menu == "View Records":
    st.subheader("Meter Records")

    df = pd.read_sql_query(
        "SELECT * FROM meters", conn
    )

    st.dataframe(df, use_container_width=True)

conn.close()