# =====================================
# STEP 1: Import Required Libraries
# =====================================
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import pytz
import re


# =====================================
# STEP 2: Load Dataset
# =====================================
df = pd.read_csv("play store data.csv")


# =====================================
# STEP 3: Data Cleaning
# =====================================

# Clean Installs
df['Installs'] = (
    df['Installs']
    .astype(str)
    .str.replace('[+,]', '', regex=True)
)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Clean Reviews
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Convert Size to MB
def convert_size(size):
    if isinstance(size, str):
        if size.endswith('M'):
            return float(size.replace('M', ''))
        elif size.endswith('k'):
            return float(size.replace('k', '')) / 1024
    return None

df['Size_MB'] = df['Size'].apply(convert_size)

# Convert Last Updated to datetime
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')
df['Month'] = df['Last Updated'].dt.to_period('M').dt.to_timestamp()

# Remove app names with numbers
df = df[~df['App'].astype(str).str.contains(r'\d', regex=True)]


# =====================================
# STEP 4: Apply Filters
# =====================================
filtered_df = df[
    (df['Rating'] >= 4.2) &
    (df['Reviews'] > 1000) &
    (df['Size_MB'] >= 20) &
    (df['Size_MB'] <= 80) &
    (df['Category'].str.startswith(('T', 'P'), na=False))
]


# =====================================
# STEP 5: Aggregate Monthly Installs
# =====================================
monthly_data = (
    filtered_df
    .groupby(['Month', 'Category'], as_index=False)
    .agg(Monthly_Installs=('Installs', 'sum'))
)

monthly_pivot = monthly_data.pivot(
    index='Month',
    columns='Category',
    values='Monthly_Installs'
).fillna(0)

# Cumulative installs
cumulative_data = monthly_pivot.cumsum()


# =====================================
# STEP 6: Month-over-Month Growth (>25%)
# =====================================
mom_growth = cumulative_data.pct_change()
highlight_months = (mom_growth > 0.25).any(axis=1)


# =====================================
# STEP 7: Translate Legend Labels
# =====================================
category_translation = {
    'Travel & Local': 'Voyage et Local',     # French
    'Productivity': 'Productividad',         # Spanish
    'Photography': '写真'                     # Japanese
}

translated_labels = [
    category_translation.get(cat, cat)
    for cat in cumulative_data.columns
]


# =====================================
# STEP 8: Time Restriction (4 PM – 6 PM IST)
# =====================================
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()

start_time = time(10, 0)  # 4 PM
end_time   = time(18, 0)  # 6 PM

print("Current IST Time:", current_time)


# =====================================
# STEP 9: Stacked Area Chart
# =====================================
if start_time <= current_time <= end_time:

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.stackplot(
        cumulative_data.index,
        cumulative_data.T,
        labels=translated_labels,
        alpha=0.8
    )

    # Highlight high-growth months
    for month in cumulative_data.index[highlight_months]:
        ax.axvspan(month, month, color='black', alpha=0.08)

    ax.set_title("Cumulative Installs Over Time by Category")
    ax.set_xlabel("Time")
    ax.set_ylabel("Cumulative Installs")

    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.show()

else:
    print("⏰ Visualization visible only between 4 PM and 6 PM IST.")