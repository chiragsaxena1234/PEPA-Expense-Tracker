import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date
# Load custom CSS
with open("style.css", "r", encoding="utf-8") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

st.set_page_config(
    page_title="Personal Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

FILE = "data/expenses.csv"

# Professional Dashboard Header

st.markdown("""
<div style="
    background: linear-gradient(120deg, #172554, #0F766E);
    padding: 28px;
    border-radius: 16px;
    margin-bottom: 25px;
">
    <h1 style="color: white; margin: 0;">
        💰 Personal Expense Pattern Analysis
    </h1>
    <p style="color: #D1FAE5; font-size: 17px; margin-bottom: 0;">
        Track your spending. Understand your habits. Manage your money.
    </p>
</div>
""", unsafe_allow_html=True)

st.caption(f"📅 Today's Date: {date.today().strftime('%d %B %Y')}")

# Load dataset
import os

os.makedirs(os.path.dirname(FILE) or ".", exist_ok=True)

if not os.path.exists(FILE):
    pd.DataFrame(columns=[
        "Date", "Category", "Description",
        "Amount", "Payment_Mode"
    ]).to_csv(FILE, index=False)

df = pd.read_csv(FILE)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
df = df.dropna(subset=["Date", "Amount", "Category"])


# Add Expense Form
st.sidebar.header("➕ Add New Expense")

with st.sidebar.form("expense_form"):
    date = st.date_input("Date")
    category = st.selectbox(
        "Category",
        ["Food", "Travel", "Education", "Shopping",
         "Entertainment", "Bills", "Other"]
    )
    description = st.text_input("Description")
    amount = st.number_input("Amount (₹)", min_value=1.0)
    payment = st.selectbox(
        "Payment Mode", ["UPI", "Cash", "Card"]
    )

    submitted = st.form_submit_button("Add Expense")

    if submitted:
        if description.strip():
            new_expense = pd.DataFrame([{
                "Date": date.strftime("%Y-%m-%d"),
                "Category": category,
                "Description": description,
                "Amount": amount,
                "Payment_Mode": payment
            }])

            new_expense.to_csv(
                FILE,
                mode="a",
                header=not os.path.exists(FILE),
                index=False
            )

            st.success("Expense added successfully!")
            st.rerun()
        else:
            st.error("Please enter a description.")

# Summary
st.subheader("📊 Expense Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Total Expenses", f"₹{df['Amount'].sum():,.2f}")
col2.metric("Total Transactions", len(df))
col3.metric(
    "Average Expense",
    f"₹{df['Amount'].mean():,.2f}" if len(df) else "₹0"
)


st.subheader("📈 Category-wise Expenses")

category_data = df.groupby("Category")["Amount"].sum()

if category_data.empty:
    st.info("No expense data available yet. Add your first expense to see charts.")

else:
    left, right = st.columns(2)

    with left:
        fig, ax = plt.subplots()
        category_data.plot(kind="bar", ax=ax)
        ax.set_ylabel("Amount (₹)")
        ax.set_title("Spending by Category")
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with right:
        fig, ax = plt.subplots()
        category_data.plot(kind="pie", autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")
        ax.set_title("Expense Distribution")
        st.pyplot(fig)
        plt.close(fig)

# Expense Records
st.subheader("📋 All Expense Records")
st.dataframe(df, use_container_width=True)

# Download
st.download_button(
    "📥 Download Expense Report",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="expense_report.csv",
    mime="text/csv"
)

# Monthly Expense Analysis
st.subheader("📅 Monthly Expense Analysis")

# Create month column
df["Month"] = df["Date"].dt.to_period("M").astype(str)

# Calculate monthly expenses
monthly_data = df.groupby("Month")["Amount"].sum().sort_index()

# Display monthly totals
st.write("### 💰 Month-wise Total Expenses")
st.dataframe(
    monthly_data.reset_index().rename(
        columns={"Month": "Month", "Amount": "Total Expenses (₹)"}
    ),
    use_container_width=True
)

# Display monthly chart
st.write("### 📊 Monthly Spending Chart")

if monthly_data.empty:
    st.info("No monthly expense data available yet. Add expenses to see this chart.")

else:
    fig, ax = plt.subplots()
    monthly_data.plot(kind="bar", ax=ax)
    ax.set_xlabel("Month")
    ax.set_ylabel("Expenses (₹)")
    ax.set_title("Monthly Expense Analysis")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

# Monthly Budget Alert
st.subheader("💰 Monthly Budget Alert")

budget = st.number_input(
    "Set Your Monthly Budget (₹)",
    min_value=100,
    value=5000,
    step=500
)

current_month = pd.Timestamp.today().strftime("%Y-%m")

current_month_expenses = df[
    df["Date"].dt.strftime("%Y-%m") == current_month
]["Amount"].sum()

remaining = budget - current_month_expenses

col1, col2 = st.columns(2)

col1.metric("This Month's Spending", f"₹{current_month_expenses:,.2f}")
col2.metric("Remaining Budget", f"₹{remaining:,.2f}")

progress = min(current_month_expenses / budget, 1.0)
st.progress(progress)

if current_month_expenses > budget:
    st.error("⚠️ Budget exceeded! Try to control your expenses.")
elif current_month_expenses >= budget * 0.8:
    st.warning("⚠️ Alert! You have used 80% of your budget.")
else:
    st.success("✅ You are within your budget!")

    # Smart Expense Insights
st.subheader("🧠 Smart Expense Insights")

if not df.empty:
    category_totals = df.groupby("Category")["Amount"].sum()

    highest_category = category_totals.idxmax()
    highest_amount = category_totals.max()

    col1, col2 = st.columns(2)

    col1.metric("🏆 Highest Spending Category", highest_category)
    col2.metric("💸 Amount Spent", f"₹{highest_amount:,.2f}")

    st.info(
        f"You spend the most on {highest_category}, "
        f"with total expenses of ₹{highest_amount:,.2f}."
    )
else:
    st.info("Add some expenses to see your spending insights.")

    # Expense Filters
st.subheader("🔎 Expense Filters")

if not df.empty:
    col1, col2 = st.columns(2)

    with col1:
        categories = ["All"] + sorted(df["Category"].dropna().unique().tolist())
        selected_category = st.selectbox(
            "Select Category",
            categories
        )

    with col2:
        min_date = df["Date"].min().date()
        max_date = df["Date"].max().date()

        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

    filtered_df = df.copy()

    if selected_category != "All":
        filtered_df = filtered_df[
            filtered_df["Category"] == selected_category
        ]

    if len(date_range) == 2:
        start_date, end_date = date_range

        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date) &
            (filtered_df["Date"].dt.date <= end_date)
        ]

    st.metric(
        "Filtered Total Expenses",
        f"₹{filtered_df['Amount'].sum():,.2f}"
    )

    st.write("### 📋 Filtered Expense Records")
    st.dataframe(filtered_df, use_container_width=True)

    st.write(f"Total matching transactions: {len(filtered_df)}")

else:
    st.info("Please add expenses to use filters.")

    # Daily Spending Analysis
st.subheader("📆 Daily Spending Analysis")

if not df.empty:
    daily_data = (
        df.groupby(df["Date"].dt.date)["Amount"]
        .sum()
        .sort_index()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Average Daily Spending",
        f"₹{daily_data.mean():,.2f}"
    )

    col2.metric(
        "Highest Daily Spending",
        f"₹{daily_data.max():,.2f}"
    )

    col3.metric(
        "Total Days with Expenses",
        len(daily_data)
    )

    st.write("### 📊 Daily Expense Chart")

    fig, ax = plt.subplots(figsize=(10, 4))
    daily_data.plot(kind="line", marker="o", ax=ax)

    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Daily Spending Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()

    st.pyplot(fig)
    plt.close(fig)

    st.write("### 📋 Daily Expense Summary")

    daily_table = daily_data.reset_index()
    daily_table.columns = ["Date", "Total Expenses (₹)"]

    st.dataframe(daily_table, use_container_width=True)

else:
    st.info("Add some expenses to see daily analysis.")

# Monthly Spending Comparison

st.subheader("📊 Monthly Spending Comparison")

df["Month"] = df["Date"].dt.to_period("M").astype(str)

monthly_data = df.groupby("Month")["Amount"].sum().sort_index()

if len(monthly_data) >= 2:
    current_month = monthly_data.iloc[-1]
    previous_month = monthly_data.iloc[-2]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Current Month",
            f"₹{current_month:.2f}"
        )

    with col2:
        st.metric(
            "Previous Month",
            f"₹{previous_month:.2f}",
            delta=f"₹{current_month - previous_month:.2f}",
            delta_color="inverse"
        )

    st.bar_chart(monthly_data)

else:
    st.info(
        "Comparison ke liye kam se kam 2 months ka expense data add karein."
    )

# PDF Expense Report

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

st.subheader("📄 Download PDF Expense Report")

if not df.empty:
    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("Personal Expense Pattern Analysis", styles["Title"]),
        Spacer(1, 15),
        Paragraph(
            f"Total Expenses: Rs. {df['Amount'].sum():.2f}",
            styles["Heading2"]
        ),
        Spacer(1, 15)
    ]

    table_data = [[
        "Date", "Category", "Description", "Amount", "Payment Mode"
    ]]

    for _, row in df.iterrows():
        table_data.append([
            str(row["Date"].date()),
            str(row["Category"]),
            str(row["Description"]),
            f"Rs. {row['Amount']:.2f}",
            str(row["Payment_Mode"])
        ])

    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "TOP")
    ]))

    elements.append(table)
    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        "⬇️ Download PDF Report",
        data=buffer.getvalue(),
        file_name="PEPA_Expense_Report.pdf",
        mime="application/pdf"
    )
else:
    st.info("PDF report ke liye pehle expense add karein.")

    # Excel Expense Report

st.subheader("📗 Download Excel Expense Report")

if not df.empty:
    excel_buffer = BytesIO()

    export_df = df[
        ["Date", "Category", "Description", "Amount", "Payment_Mode"]
    ].copy()

    export_df["Date"] = export_df["Date"].dt.strftime("%Y-%m-%d")

    with pd.ExcelWriter(
        excel_buffer, engine="openpyxl"
    ) as writer:
        export_df.to_excel(
            writer, index=False, sheet_name="Expenses"
        )

        worksheet = writer.sheets["Expenses"]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for column_cells in worksheet.columns:
            max_length = max(
                len(str(cell.value or ""))
                for cell in column_cells
            )
            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = min(max_length + 2, 30)

    st.download_button(
        label="⬇️ Download Excel Report",
        data=excel_buffer.getvalue(),
        file_name="PEPA_Expense_Report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Excel report download karne ke liye pehle expense add karein.")

    # Interactive Spending Trends

import plotly.express as px

st.header("📈 Interactive Spending Trends")

if not df.empty:
    chart_df = df.copy()

    chart_df["Month"] = (
        chart_df["Date"].dt.to_period("M").astype(str)
    )
    chart_df["Day"] = chart_df["Date"].dt.strftime("%Y-%m-%d")

    chart_type = st.selectbox(
        "Choose Spending Analysis",
        [
            "Monthly Spending",
            "Category-wise Spending",
            "Daily Spending"
        ]
    )

    if chart_type == "Monthly Spending":
        monthly = (
            chart_df.groupby("Month")["Amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            monthly,
            x="Month",
            y="Amount",
            title="Monthly Expense Trends",
            text_auto=".2f",
            color="Amount",
            labels={"Amount": "Expenses (₹)"}
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Category-wise Spending":
        category = (
            chart_df.groupby("Category")["Amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            category,
            names="Category",
            values="Amount",
            title="Expenses by Category",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Daily Spending":
        daily = (
            chart_df.groupby("Day")["Amount"]
            .sum()
            .reset_index()
            .sort_values("Day")
        )

        fig = px.line(
            daily,
            x="Day",
            y="Amount",
            title="Daily Spending Trend",
            markers=True,
            labels={
                "Day": "Date",
                "Amount": "Expenses (₹)"
            }
        )

        st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Charts dekhne ke liye pehle expenses add karein.")

    # Expense Prediction

st.header("🔮 Next Month Expense Prediction")

if not df.empty:
    prediction_df = df.copy()

    prediction_df["MonthPeriod"] = (
        prediction_df["Date"].dt.to_period("M")
    )

    monthly_expenses = (
        prediction_df.groupby("MonthPeriod")["Amount"]
        .sum()
        .sort_index()
    )

    if len(monthly_expenses) >= 2:

        # Last 3 available months ka average
        recent_expenses = monthly_expenses.tail(3)
        predicted_expense = recent_expenses.mean()

        # Latest recorded month ke agle month ki date
        next_month = monthly_expenses.index[-1] + 1

        st.metric(
            "Estimated Next Month Expense",
            f"₹{predicted_expense:,.2f}"
        )

        st.caption(
            "Prediction pichhle 3 available months ke average "
            "par based hai (ya data kam ho to available months par)."
        )

        # Actual aur predicted expenses ka chart
        chart_data = pd.DataFrame({
            "Month": (
                [str(month) for month in monthly_expenses.index]
                + [str(next_month)]
            ),
            "Amount": (
                monthly_expenses.tolist()
                + [predicted_expense]
            ),
            "Type": (
                ["Actual"] * len(monthly_expenses)
                + ["Predicted"]
            )
        })

        fig = px.bar(
            chart_data,
            x="Month",
            y="Amount",
            color="Type",
            barmode="group",
            title="Actual vs Predicted Expenses",
            labels={"Amount": "Expenses (₹)"}
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.info(
            "Prediction ke liye kam se kam 2 different "
            "months ka expense data add karein."
        )

else:
    st.info("Prediction ke liye pehle expenses add karein.")

    # Budget vs Prediction Alert

st.header("🚨 Budget vs Prediction Alert")

monthly_budget = st.number_input(
    "Set Your Monthly Budget (₹)",
    min_value=0.0,
    value=5000.0,
    step=500.0
)

if not df.empty:
    budget_df = df.copy()

    budget_df["MonthPeriod"] = (
        budget_df["Date"].dt.to_period("M")
    )

    monthly_totals = (
        budget_df.groupby("MonthPeriod")["Amount"]
        .sum()
        .sort_index()
    )

    if len(monthly_totals) >= 2:
        predicted = monthly_totals.tail(3).mean()

        st.metric(
            "Predicted Monthly Expense",
            f"₹{predicted:,.2f}"
        )

        st.metric(
            "Monthly Budget",
            f"₹{monthly_budget:,.2f}"
        )

        if predicted > monthly_budget:
            st.error(
                f"⚠️ Warning! Estimated expense budget se "
                f"₹{predicted - monthly_budget:,.2f} zyada hai."
            )
        else:
            st.success(
                f"✅ Good! Estimated expense budget ke andar hai. "
                f"Remaining: ₹{monthly_budget - predicted:,.2f}"
            )
    else:
        st.info(
            "Budget prediction ke liye kam se kam "
            "2 different months ka data add karein."
        )
else:
    st.info("Pehle apne expenses add karein.")

    # PEPA Sidebar Navigation

st.sidebar.markdown("## 💰 PEPA")
st.sidebar.caption("Personal Finance Dashboard")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧭 Quick Navigation")

st.sidebar.markdown(
    "[🏠 Dashboard](#personal-expense-pattern-analysis)"
)

st.sidebar.markdown(
    "[📊 Spending Trends](#interactive-spending-trends)"
)

st.sidebar.markdown(
    "[🔮 Expense Prediction](#next-month-expense-prediction)"
)

st.sidebar.markdown(
    "[🚨 Budget Alerts](#budget-vs-prediction-alert)"
)

st.sidebar.markdown(
    "[📄 PDF Report](#download-pdf-expense-report)"
)

st.sidebar.markdown(
    "[📗 Excel Report](#download-excel-expense-report)"
)

st.sidebar.markdown("---")
st.sidebar.caption("Track smarter. Spend wiser. 💚")

# ==============================
# 🎯 Savings Goal Tracker
# ==============================

import json
from pathlib import Path

GOAL_FILE = Path("data/savings_goal.json")

# Load previously saved goal
if GOAL_FILE.exists():
    try:
        with open(GOAL_FILE, "r", encoding="utf-8") as file:
            goal_data = json.load(file)
    except (json.JSONDecodeError, OSError):
        goal_data = {"target": 5000, "saved": 0}
else:
    goal_data = {"target": 5000, "saved": 0}

st.markdown("---")
st.header("🎯 Savings Goal Tracker")
st.write("Set your savings target and track your progress.")

with st.form("savings_goal_form"):
    target = st.number_input(
        "🎯 Savings Target (₹)",
        min_value=1.0,
        value=float(goal_data["target"]),
        step=500.0
    )

    saved = st.number_input(
        "💰 Amount Saved So Far (₹)",
        min_value=0.0,
        value=float(goal_data["saved"]),
        step=100.0
    )

    save_goal = st.form_submit_button("💾 Save Goal")

if save_goal:
    GOAL_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(GOAL_FILE, "w", encoding="utf-8") as file:
        json.dump(
            {"target": target, "saved": saved},
            file,
            indent=4
        )

    st.success("Savings goal saved successfully!")
    st.rerun()

# Show saved goal details
progress = min(saved / target, 1.0)
remaining = max(target - saved, 0)

st.subheader("📊 Your Savings Progress")

st.progress(progress)
st.write(f"**Progress:** {progress * 100:.1f}%")

col1, col2, col3 = st.columns(3)

col1.metric("🎯 Target", f"₹{target:,.0f}")
col2.metric("💰 Saved", f"₹{saved:,.0f}")
col3.metric("📌 Remaining", f"₹{remaining:,.0f}")

if saved >= target:
    st.success("🎉 Congratulations! Your savings goal is complete!")
else:
    st.info(f"Keep going! ₹{remaining:,.0f} more to reach your goal.")

    # =====================================
# 🚨 Unusual Spending Detector
# =====================================

st.markdown("---")
st.header("🚨 Unusual Spending Detector")
st.write(
    "Detect categories where daily spending is "
    "much higher than the usual level."
)

try:
    expense_data = pd.read_csv("data/expenses.csv")

    required_columns = {"Date", "Category", "Amount"}

    if not required_columns.issubset(expense_data.columns):
        st.error("CSV must contain Date, Category and Amount columns.")

    elif expense_data.empty:
        st.info("Add some expenses to detect unusual spending.")

    else:
        expense_data["Date"] = pd.to_datetime(
            expense_data["Date"], errors="coerce"
        )
        expense_data["Amount"] = pd.to_numeric(
            expense_data["Amount"], errors="coerce"
        )

        expense_data = expense_data.dropna(
            subset=["Date", "Category", "Amount"]
        )

        # Total spending per category per day
        daily_data = (
            expense_data.groupby(
                [expense_data["Date"].dt.date, "Category"]
            )["Amount"]
            .sum()
            .reset_index()
        )

        daily_data.columns = ["Date", "Category", "Daily_Total"]

        alerts = []

        # Compare each day with other days in the same category
        for category in daily_data["Category"].unique():
            category_data = daily_data[
                daily_data["Category"] == category
            ]

            for _, current in category_data.iterrows():
                previous_days = category_data[
                    category_data["Date"] != current["Date"]
                ]

                if len(previous_days) < 2:
                    continue

                average = previous_days["Daily_Total"].mean()

                if average > 0 and current["Daily_Total"] > average * 1.5:
                    alerts.append({
                        "Date": current["Date"],
                        "Category": category,
                        "Spent": current["Daily_Total"],
                        "Usual Average": average
                    })

        if alerts:
            st.warning(
                f"Found {len(alerts)} potentially unusual "
                "spending day(s)."
            )

            alert_df = pd.DataFrame(alerts)
            alert_df["Extra Spending"] = (
                alert_df["Spent"] - alert_df["Usual Average"]
            )

            st.dataframe(
                alert_df.style.format({
                    "Spent": "₹{:,.2f}",
                    "Usual Average": "₹{:,.2f}",
                    "Extra Spending": "₹{:,.2f}"
                }),
                use_container_width=True
            )

            st.caption(
                "An alert means spending was over 1.5 times "
                "the average of other recorded days in that category. "
                "It is a warning, not proof of a mistake."
            )

        else:
            st.success(
                "No unusual spending detected with the current data."
            )
            st.caption(
                "At least three recorded days in a category are "
                "needed for this comparison."
            )

except FileNotFoundError:
    st.error("Expense file not found: data/expenses.csv")

except Exception as e:
    st.error(f"Could not analyze expenses: {e}")

    