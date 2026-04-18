# Daily Savings Strategy App

A Streamlit + SQLite web app that helps you follow a **365-day savings plan**:

- Start at $1 on January 1st
- Increase by $1 each day
- End at $365 on December 31st
- Total savings: **$66,795** (or **$67,161** in leap years)

The app lets you query any date, input actual savings, visualize progress, track milestones, and export your data.

---

## 🚀 Features

- **Daily savings calculator**: Shows expected savings for each day.
- **Cumulative tracker**: Displays expected total saved so far.
- **Actual savings input**: Enter how much you really saved each day.
- **Comparison vs expected**: See if you’re ahead, behind, or on track.
- **Catch‑up suggestions**: If behind, app calculates extra per day needed to get back on track.
- **Progress bar**: Percentage of yearly goal achieved.
- **Milestone tracker**:
  - Quarterly checkpoints (Day 91, 182, 273, Year-end).
  - Monthly checkpoints (Day 30, 60, 90, …).
- **Charts**:
  - Line chart of expected vs actual cumulative savings.
- **Export options**:
  - Download savings data as CSV or Excel (generated in memory, no filesystem writes).
- **Leap year support**: Automatically adjusts to 366 days.

---

## 📦 Dependencies

Install required packages:

```bash
python -m pip install --upgrade pip
pip install pandas streamlit matplotlib openpyxl
