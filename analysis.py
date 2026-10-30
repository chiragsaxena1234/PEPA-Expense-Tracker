import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("data/expenses.csv")

# Total expenses
total = df["Amount"].sum()
print("Total Expenses:", total)

# Category-wise expenses
category = df.groupby("Category")["Amount"].sum()

print("\nCategory-wise Expenses:")
print(category)

# Highest spending category
highest = category.idxmax()

print("\nHighest Spending Category:", highest)
print("Amount Spent:", category.max())

# Average expense
print("\nAverage Expense:", round(df["Amount"].mean(), 2))

# Create charts
plt.figure(figsize=(12, 5))

# Bar chart
plt.subplot(1, 2, 1)
category.plot(kind="bar")
plt.title("Category-wise Expenses")
plt.xlabel("Category")
plt.ylabel("Amount (Rs.)")
plt.xticks(rotation=45)

# Pie chart
plt.subplot(1, 2, 2)
category.plot(kind="pie", autopct="%1.1f%%")
plt.title("Expense Distribution")
plt.ylabel("")

plt.tight_layout()
plt.show()