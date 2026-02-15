# =====================================
# STEP 1: Import Required Libraries
# =====================================
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import pytz


# =====================================
# STEP 2: Load Dataset
# =====================================
df = pd.read_csv("play store data.csv")


# =====================================
# STEP 3: Data Cleaning
# =====================================

# Clean Installs
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Clean Price
df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=True)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)

# Revenue calculation
df['Revenue'] = df['Installs'] * df['Price']

# Convert Size to MB
def convert_size(size):
    if isinstance(size, str):
        if size.endswith('M'):
            return float(size.replace('M', ''))
        if size.endswith('k'):
            return float(size.replace('k', '')) / 1024
    return None

df['Size_MB'] = df['Size'].apply(convert_size)

# Extract Android Version
df['Android_Version'] = (
    df['Android Ver']
    .astype(str)
    .str.extract(r'(\d+\.\d+|\d+)')
)
df['Android_Version'] = pd.to_numeric(df['Android_Version'], errors='coerce')

# App name length
df['App_Length'] = df['App'].astype(str).apply(len)


# =====================================
# STEP 4: APPLY CORRECT FILTERS ✅
# =====================================
filtered_df = df[
    (df['Installs'] >= 10000) &
    (
        ((df['Type'] == 'Paid') & (df['Revenue'] >= 10000)) |
        (df['Type'] == 'Free')
    ) &
    (df['Android_Version'] > 4.0) &
    (df['Size_MB'] > 15) &
    (df['Content Rating'] == 'Everyone') &
    (df['App_Length'] <= 30)
]


# =====================================
# STEP 5: Top 3 Categories by Installs
# =====================================
top_categories = (
    filtered_df
    .groupby('Category')['Installs']
    .sum()
    .sort_values(ascending=False)
    .head(3)
    .index
)


# =====================================
# STEP 6: Aggregate Free vs Paid
# =====================================
summary = (
    filtered_df[filtered_df['Category'].isin(top_categories)]
    .groupby(['Category', 'Type'], as_index=False)
    .agg(
        Avg_Installs=('Installs', 'mean'),
        Avg_Revenue=('Revenue', 'mean')
    )
)


# =====================================
# STEP 7: Time Restriction (1 PM – 2 PM IST)
# =====================================
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()

start_time = time(13, 0)
end_time   = time(14, 0)

print("Current IST Time:", current_time)


# =====================================
# STEP 8: Dual-Axis Chart
# =====================================
if start_time <= current_time <= end_time:

    if summary.empty:
        print("❌ No data available after applying filters.")
    else:
        labels = summary['Category'] + " (" + summary['Type'] + ")"
        x = range(len(labels))

        fig, ax1 = plt.subplots(figsize=(10, 5))

        # Bar: Avg Installs
        ax1.bar(x, summary['Avg_Installs'])
        ax1.set_ylabel("Average Installs")

        # Line: Avg Revenue
        ax2 = ax1.twinx()
        ax2.plot(x, summary['Avg_Revenue'], marker='o')
        ax2.set_ylabel("Average Revenue ($)")

        ax1.set_xticks(x)
        ax1.set_xticklabels(labels, rotation=45, ha='right')

        plt.title("Average Installs vs Revenue (Free vs Paid Apps)")
        plt.tight_layout()
        plt.show()

else:
    print("⏰ Graph hidden (Visible only between 1 PM and 2 PM IST).")