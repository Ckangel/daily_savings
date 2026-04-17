import sqlite3
import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import io

# -----------------------------
# Database Setup
# -----------------------------
def init_db(year):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS savings (
            day INTEGER PRIMARY KEY,
            date TEXT,
            amount INTEGER,
            cumulative INTEGER
        )
    """)
    conn.commit()
    conn.close()

def populate_db(year):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    start_date = datetime.date(year, 1, 1)
    cumulative = 0
    days_in_year = 366 if is_leap_year(year) else 365

    for day in range(1, days_in_year + 1):
        amount = day
        cumulative += amount
        date = start_date + datetime.timedelta(days=day-1)
        c.execute("INSERT OR REPLACE INTO savings VALUES (?, ?, ?, ?)",
                  (day, str(date), amount, cumulative))
    conn.commit()
    conn.close()

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# -----------------------------
# Query Function
# -----------------------------
def get_savings_by_date(query_date):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute("SELECT day, amount, cumulative FROM savings WHERE date=?", (str(query_date),))
    result = c.fetchone()
    conn.close()
    return result

def get_all_savings():
    conn = sqlite3.connect("savings.db")
    df = pd.read_sql_query("SELECT * FROM savings", conn)
    conn.close()
    return df

# -----------------------------
# Streamlit App
# -----------------------------
def main():
    st.title("365-Day Daily Savings Strategy")

    year = datetime.date.today().year
    init_db(year)
    populate_db(year)

    # Date input
    query_date = st.date_input("Select a date", datetime.date.today())
    result = get_savings_by_date(query_date)

    if result:
        day, amount, cumulative = result
        st.write(f"📅 Day {day} ({query_date})")
        st.write(f"💵 Amount to save today: ${amount}")
        st.write(f"📊 Total saved so far: ${cumulative}")
    else:
        st.warning("Date not found in savings plan.")

    # Show year-end total
    days_in_year = 366 if is_leap_year(year) else 365
    total = days_in_year * (days_in_year + 1) // 2
    st.write(f"🎯 Total by year end: ${total}")

    # Chart
    df = get_all_savings()
    fig, ax = plt.subplots()
    ax.plot(df["day"], df["cumulative"], label="Cumulative Savings")
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Cumulative Savings ($)")
    ax.set_title("Cumulative Savings Progress")
    ax.legend()
    st.pyplot(fig)

    # Export buttons (no filesystem writes)
    # CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download CSV", csv_buffer.getvalue(),
                       "savings_data.csv", "text/csv")

    # Excel
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    st.download_button("Download Excel", excel_buffer.getvalue(),
                       "savings_data.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
