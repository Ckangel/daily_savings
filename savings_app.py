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
    # Drop old table if it exists (to avoid mismatch errors)
    c.execute("DROP TABLE IF EXISTS savings")
    # Create new table with 6 columns
    c.execute("""
        CREATE TABLE savings (
            day INTEGER PRIMARY KEY,
            date TEXT,
            amount INTEGER,
            cumulative INTEGER,
            actual INTEGER,
            actual_cumulative INTEGER
        )
    """)
    conn.commit()
    conn.close()

def populate_db(year):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    start_date = datetime.date(year, 1, 1)
    cumulative = 0
    actual_cumulative = 0
    days_in_year = 366 if is_leap_year(year) else 365

    for day in range(1, days_in_year + 1):
        amount = day
        cumulative += amount
        date = start_date + datetime.timedelta(days=day-1)
        actual = amount  # default actual = expected
        actual_cumulative += actual
        c.execute("INSERT OR REPLACE INTO savings VALUES (?, ?, ?, ?, ?, ?)",
                  (day, str(date), amount, cumulative, actual, actual_cumulative))
    conn.commit()
    conn.close()

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# -----------------------------
# Query Functions
# -----------------------------
def get_savings_by_date(query_date):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute("SELECT day, amount, cumulative, actual, actual_cumulative FROM savings WHERE date=?", (str(query_date),))
    result = c.fetchone()
    conn.close()
    return result

def update_actual_savings(query_date, actual_amount):
    conn = sqlite3.connect("savings.db")
    c = conn.cursor()
    c.execute("SELECT day, amount FROM savings WHERE date=?", (str(query_date),))
    row = c.fetchone()
    if row:
        day, expected = row
        c.execute("UPDATE savings SET actual=? WHERE day=?", (actual_amount, day))
        df = pd.read_sql_query("SELECT * FROM savings ORDER BY day", conn)
        df.loc[df["day"] == day, "actual"] = actual_amount
        df["actual_cumulative"] = df["actual"].cumsum()
        for _, r in df.iterrows():
            c.execute("UPDATE savings SET actual=?, actual_cumulative=? WHERE day=?",
                      (int(r["actual"]), int(r["actual_cumulative"]), int(r["day"])))
    conn.commit()
    conn.close()

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

    query_date = st.date_input("Select a date", datetime.date.today())
    result = get_savings_by_date(query_date)

    days_in_year = 366 if is_leap_year(year) else 365
    yearly_goal = days_in_year * (days_in_year + 1) // 2

    if result:
        day, expected, cumulative, actual, actual_cumulative = result
        st.write(f"📅 Day {day} ({query_date})")
        st.write(f"💵 Expected to save today: ${expected}")
        st.write(f"📊 Expected cumulative savings: ${cumulative}")
        st.write(f"💰 Actual saved today: ${actual}")
        st.write(f"📊 Actual cumulative savings: ${actual_cumulative}")

        outstanding = cumulative - actual_cumulative
        if outstanding > 0:
            st.warning(f"⚠️ You are behind by ${outstanding} compared to expected YTD savings.")

            # Catch-up suggestion
            days_left = days_in_year - day
            if days_left > 0:
                extra_per_day = outstanding / days_left
                st.info(f"💡 To catch up, save an extra ${extra_per_day:.2f} per day for the remaining {days_left} days.")
        elif outstanding < 0:
            st.success(f"✅ You are ahead by ${-outstanding} compared to expected YTD savings.")
        else:
            st.info("🎯 You are exactly on track!")

        # Progress Tracker Bar
        progress = actual_cumulative / yearly_goal
        st.progress(progress)
        st.write(f"Progress: {progress:.2%} of yearly goal")

        # Input actual savings
        new_actual = st.number_input("Enter actual amount saved today", min_value=0, value=actual)
        if st.button("Update Actual Savings"):
            update_actual_savings(query_date, new_actual)
            st.success("Actual savings updated successfully! Refresh to see changes.")

    else:
        st.warning("Date not found in savings plan.")

    st.write(f"🎯 Total yearly goal: ${yearly_goal}")

    # Chart
    df = get_all_savings()
    fig, ax = plt.subplots()
    ax.plot(df["day"], df["cumulative"], label="Expected Savings", linestyle="--")
    ax.plot(df["day"], df["actual_cumulative"], label="Actual Savings", color="green")
    ax.set_xlabel("Day of Year")
    ax.set_ylabel("Cumulative Savings ($)")
    ax.set_title("Cumulative Savings Progress")
    ax.legend()
    st.pyplot(fig)

    # Export buttons
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button("Download CSV", csv_buffer.getvalue(),
                       "savings_data.csv", "text/csv")

    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    st.download_button("Download Excel", excel_buffer.getvalue(),
                       "savings_data.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

if __name__ == "__main__":
    main()
