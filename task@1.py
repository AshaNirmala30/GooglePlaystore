import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import pytz

# -------------------------------
# 1. LOAD DATA
# -------------------------------
# Dataset name updated as requested
df = pd.read_csv("play Store Data.csv")

# -------------------------------
# 2. DATA CLEANING
# -------------------------------

# Convert Rating to numeric
df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

# Convert Reviews to numeric
df['Reviews'] = pd.to_numeric(df['Reviews'], errors='coerce')

# Convert Installs (remove + and ,)
df['Installs'] = df['Installs'].str.replace('[+,]', '', regex=True)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Convert Size (remove 'M')
df['Size'] = df['Size'].str.replace('M', '', regex=False)
df['Size'] = pd.to_numeric(df['Size'], errors='coerce')

# Convert Last Updated to datetime
df['Last Updated'] = pd.to_datetime(df['Last Updated'], errors='coerce')

# -------------------------------
# 3. FILTER CONDITIONS
# -------------------------------

filtered_df = df[
    (df['Rating'] >= 4.0) &
    (df['Size'] >= 10) &
    (df['Last Updated'].dt.month == 1)
]

# -------------------------------
# 4. GROUP BY CATEGORY
# -------------------------------

category_stats = filtered_df.groupby('Category').agg(
    Avg_Rating=('Rating', 'mean'),
    Total_Reviews=('Reviews', 'sum'),
    Total_Installs=('Installs', 'sum')
).reset_index()

# Top 10 categories by installs
top_10 = category_stats.sort_values(
    by='Total_Installs', ascending=False
).head(10)

# -------------------------------
# 5. TIME CONDITION (3 PM – 5 PM IST)
# -------------------------------

ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()

start_time = datetime.strptime("15:00", "%H:%M").time()
end_time = datetime.strptime("17:00", "%H:%M").time()

if start_time <= current_time <= end_time:

    # -------------------------------
    # 6. GROUPED BAR CHART
    # -------------------------------

    x = range(len(top_10))

    plt.figure(figsize=(12, 6))
    plt.bar(x, top_10['Avg_Rating'], width=0.4, label='Average Rating')
    plt.bar(
        [i + 0.4 for i in x],
        top_10['Total_Reviews'] / 1_000_000,
        width=0.4,
        label='Total Reviews (in millions)'
    )

    plt.xticks([i + 0.2 for i in x], top_10['Category'], rotation=45)
    plt.xlabel("App Category")
    plt.ylabel("Values")
    plt.title("Top 10 App Categories: Average Rating vs Total Reviews")
    plt.legend()
    plt.tight_layout()
    plt.show()

else:
    print("⛔ Graph not available. Dashboard accessible only between 3 PM and 5 PM IST.")