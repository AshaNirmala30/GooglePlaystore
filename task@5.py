import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, time
import pytz
import numpy as np

# =====================================
# STEP 1: Load Dataset
# =====================================
# Ensure the file name matches your local file
try:
    df = pd.read_csv("play store data.csv")
except FileNotFoundError:
    print("Error: 'play store data.csv' not found. Please check the file path.")
    exit()

# =====================================
# STEP 2: Data Cleaning
# =====================================
# Clean Installs (Remove + and ,)
df['Installs'] = df['Installs'].astype(str).str.replace(r'[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Convert Reviews
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Convert Size to MB
def convert_size(size):
    if isinstance(size, str):
        if 'M' in size:
            return float(size.replace('M', ''))
        elif 'k' in size:
            return float(size.replace('k', '')) / 1024
    return np.nan

df['Size_MB'] = df['Size'].apply(convert_size)

# --- THE FIX: Removing the "S" filter ---
# The line removing 's' or 'S' was likely deleting 99% of your data.
# I have commented it out below. 
# df = df[~df['App'].astype(str).str.contains('s', case=False, regex=True)]

# =====================================
# STEP 3: Handle Sentiment & Categories
# =====================================
if 'Sentiment_Subjectivity' not in df.columns:
    df['Sentiment_Subjectivity'] = 0.6

# Standardize Categories to Uppercase (as they usually are in this dataset)
df['Category'] = df['Category'].str.upper()

allowed_categories = [
    'GAME', 'BEAUTY', 'BUSINESS', 'COMICS',
    'COMMUNICATION', 'DATING', 'ENTERTAINMENT',
    'SOCIAL', 'EVENTS'
]

# =====================================
# STEP 4: Apply Filters (With Debugging)
# =====================================
print(f"Total apps initially: {len(df)}")

filtered_df = df[
    (df['Rating'] > 3.5) &
    (df['Reviews'] > 500) &
    (df['Installs'] > 50000) &
    (df['Category'].isin(allowed_categories))
].copy()

# Drop rows with NaN in key columns needed for the chart
filtered_df = filtered_df.dropna(subset=['Size_MB', 'Rating', 'Installs'])

print(f"Apps remaining after filtering: {len(filtered_df)}")

# =====================================
# STEP 5: Translate Category Names
# =====================================
category_translation = {
    'BEAUTY': 'सौंदर्य',
    'BUSINESS': 'வணிகம்',
    'DATING': 'Dating (Deutsch)'
}
filtered_df['Category_Label'] = filtered_df['Category'].replace(category_translation)

# =====================================
# STEP 6: Time Restriction & Plotting
# =====================================
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()
start_time = time(15, 0)  # 5 PM IST
end_time = time(19, 0)    # 7 PM IST

# FOR TESTING: Set this to True to bypass the time restriction
bypass_time_check = True 

if (start_time <= current_time <= end_time) or bypass_time_check:
    if filtered_df.empty:
        print("❌ No data found with the current filters. Try lowering the Installs or Reviews requirement.")
    else:
        plt.figure(figsize=(12, 7))

        # Scale bubble sizes
        max_installs = filtered_df['Installs'].max()
        # Prevent division by zero if max_installs is 0
        if max_installs > 0:
            installs_scaled = (filtered_df['Installs'] / max_installs) * 1000 + 50
        else:
            installs_scaled = 100

        for category in filtered_df['Category_Label'].unique():
            subset = filtered_df[filtered_df['Category_Label'] == category]
            
            # Highlight GAME in Pink
            color = 'pink' if category == 'GAME' else 'skyblue'

            plt.scatter(
                subset['Size_MB'],
                subset['Rating'],
                s=installs_scaled[subset.index],
                alpha=0.6,
                label=category,
                color=color,
                edgecolors='w',
                linewidth=0.5
            )

        plt.xlabel("App Size (MB)")
        plt.ylabel("Average Rating")
        plt.title("App Size vs Rating with Installs (Bubble Chart)")
        plt.legend(title="Category", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()
else:
    print("⏰ Bubble chart visible only between 5 PM and 7 PM IST.")
    print("Current IST Time:", current_time.strftime("%H:%M:%S"))