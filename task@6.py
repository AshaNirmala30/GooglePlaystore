# =====================================
# STEP 1: Import Required Libraries
# =====================================
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import pytz
import numpy as np

# =====================================
# STEP 2: Load Dataset
# =====================================
df = pd.read_csv("play store data.csv")

# =====================================
# STEP 3: Data Cleaning
# =====================================
# Use 'Last Updated' column as date
if 'Last Updated' not in df.columns:
    raise ValueError("Dataset must contain 'Last Updated' column for time series")

df['Date'] = pd.to_datetime(df['Last Updated'], errors='coerce')

# Clean Installs
df['Installs'] = df['Installs'].astype(str).str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Clean Reviews
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Drop rows with missing critical data
df = df.dropna(subset=['Date', 'Installs', 'Reviews', 'App', 'Category'])

# =====================================
# STEP 4: Apply Filters
# =====================================
# Reviews > 500
df = df[df['Reviews'] > 500]

# App name does not start with X, Y, Z
df = df[~df['App'].str.upper().str.startswith(('X','Y','Z'))]

# App name does not contain S/s
df = df[~df['App'].str.contains('s', case=False, regex=True)]

# Category starts with E, C, B
df = df[df['Category'].str.upper().str.startswith(('E','C','B'))]

# =====================================
# STEP 5: Translate Categories
# =====================================
category_translation = {
    'Beauty': 'सौंदर्य',          # Hindi
    'Business': 'வணிகம்',         # Tamil
    'Dating': 'Dating (Deutsch)'  # German
}
df['Category_Label'] = df['Category'].replace(category_translation)

# =====================================
# STEP 6: Aggregate Total Installs by Month and Category
# =====================================
df['YearMonth'] = df['Date'].dt.to_period('M')
monthly_installs = df.groupby(['YearMonth', 'Category_Label'])['Installs'].sum().reset_index()
monthly_installs['YearMonth'] = monthly_installs['YearMonth'].dt.to_timestamp()

# Calculate month-over-month growth
monthly_installs['MoM_Growth'] = monthly_installs.groupby('Category_Label')['Installs'].pct_change() * 100

# =====================================
# STEP 7: Time Restriction (6 PM – 9 PM IST)
# =====================================
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()
start_time = time(18, 0)  # 6 PM IST
end_time   = time(21, 0)  # 9 PM IST

if start_time <= current_time <= end_time:
    # =====================================
    # STEP 8: Plot Time Series Line Chart
    # =====================================
    plt.figure(figsize=(14, 7))

    categories = monthly_installs['Category_Label'].unique()
    colors = plt.cm.tab10.colors  # up to 10 categories

    for i, category in enumerate(categories):
        subset = monthly_installs[monthly_installs['Category_Label'] == category].sort_values('YearMonth')
        plt.plot(subset['YearMonth'], subset['Installs'], label=category, color=colors[i % len(colors)], linewidth=2)

        # Shade areas where MoM growth > 20%
        growth_mask = subset['MoM_Growth'] > 20
        plt.fill_between(subset['YearMonth'], 0, subset['Installs'], where=growth_mask, color=colors[i % len(colors)], alpha=0.2)

    plt.xlabel("Month")
    plt.ylabel("Total Installs")
    plt.title("Monthly Total Installs by Category (Highlight MoM Growth > 20%)")
    plt.legend(title="Category")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
else:
    print("⏰ Time series chart visible only between 6 PM and 9 PM IST. Current IST Time:", current_time)