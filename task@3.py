# =====================================
# STEP 1: Import Required Libraries
# =====================================
import pandas as pd
import plotly.express as px
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
df['Installs'] = (
    df['Installs']
    .astype(str)
    .str.replace('[+,]', '', regex=True)
)
df['Installs'] = pd.to_numeric(df['Installs'], errors='coerce')

# Drop invalid rows
df = df.dropna(subset=['Installs', 'Category'])


# =====================================
# STEP 4: Create Dummy Country Column (FIX)
# =====================================
df['Country'] = 'India'   # Required for Choropleth


# =====================================
# STEP 5: Exclude Categories Starting with A, C, G, S
# =====================================
df = df[
    ~df['Category'].str.startswith(('A', 'C', 'G', 'S'), na=False)
]


# =====================================
# STEP 6: Select Top 5 Categories by Installs
# =====================================
top_categories = (
    df.groupby('Category')['Installs']
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
)

df = df[df['Category'].isin(top_categories)]


# =====================================
# STEP 7: Aggregate Installs
# =====================================
map_df = (
    df.groupby(['Country', 'Category'], as_index=False)
    .agg(Total_Installs=('Installs', 'sum'))
)

# Highlight installs > 1 million
map_df['Highlight'] = map_df['Total_Installs'] > 1_000_000


# =====================================
# STEP 8: Time Restriction (6 PM – 8 PM IST)
# =====================================
ist = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist).time()

start_time = time(18, 0)  # 6 PM
end_time   = time(20, 0)  # 8 PM

print("Current IST Time:", current_time)


# =====================================
# STEP 9: Interactive Choropleth Map
# =====================================
if start_time <= current_time <= end_time:

    fig = px.choropleth(
        map_df,
        locations="Country",
        locationmode="country names",
        color="Total_Installs",
        hover_name="Category",
        hover_data=["Total_Installs"],
        animation_frame="Category",
        color_continuous_scale="Plasma",
        title="Global Installs by Category (Top 5)"
    )

    fig.show()

else:
    print("⏰ Choropleth map visible only between 6 PM and 8 PM IST.")