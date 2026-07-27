import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Analytics Dashboard",
    page_icon="🦠",
    layout="wide"
)

st.title("🦠 COVID-19 Analytics Dashboard")
st.caption("Cases • Recoveries • Deaths • Vaccinations • Country Comparison")


# -------------------------------------------------------------------
# 1. GENERATE / LOAD DATA
# -------------------------------------------------------------------
@st.cache_data
def generate_sample_data():
    """Creates realistic-looking sample COVID-19 data for demo purposes."""
    np.random.seed(42)

    countries = ["India", "USA", "Brazil", "UK", "Germany",
                 "France", "Italy", "Russia", "China", "Japan"]

    dates = pd.date_range(start="2024-01-01", end="2024-06-30", freq="D")

    rows = []
    for country in countries:
        base_cases = np.random.randint(500, 5000)
        cumulative_cases = 0
        cumulative_deaths = 0
        cumulative_recovered = 0
        cumulative_vaccinated = np.random.randint(1_000_000, 5_000_000)

        for date in dates:
            new_cases = max(0, int(np.random.normal(base_cases, base_cases * 0.2)))
            new_deaths = max(0, int(new_cases * np.random.uniform(0.01, 0.03)))
            new_recovered = max(0, int(new_cases * np.random.uniform(0.85, 0.95)))
            new_vaccinated = np.random.randint(5000, 50000)

            cumulative_cases += new_cases
            cumulative_deaths += new_deaths
            cumulative_recovered += new_recovered
            cumulative_vaccinated += new_vaccinated

            rows.append({
                "Date": date,
                "Country": country,
                "Confirmed": cumulative_cases,
                "Deaths": cumulative_deaths,
                "Recovered": cumulative_recovered,
                "Vaccinated": cumulative_vaccinated
            })

    return pd.DataFrame(rows)


def load_uploaded_data(uploaded_file):
    """Loads and lightly cleans a user-uploaded CSV."""
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]  # trim column names

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Fill missing optional columns with 0 so the app doesn't break
    for col in ["Confirmed", "Deaths", "Recovered", "Vaccinated"]:
        if col not in df.columns:
            df[col] = 0

    return df


# -------------------------------------------------------------------
# 2. SIDEBAR CONTROLS
# -------------------------------------------------------------------
st.sidebar.header("⚙️ Controls")

# Always use generated sample data
df = generate_sample_data()
st.sidebar.success("Sample COVID-19 dataset loaded")

all_countries = sorted(df["Country"].unique())
selected_countries = st.sidebar.multiselect(
    "Select countries to compare",
    options=all_countries,
    default=all_countries[:5]
)

if not selected_countries:
    st.warning("Please select at least one country from the sidebar.")
    st.stop()

filtered_df = df[df["Country"].isin(selected_countries)]

if "Date" in filtered_df.columns:
    min_date, max_date = filtered_df["Date"].min(), filtered_df["Date"].max()
    date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[
            (filtered_df["Date"] >= start_date) & (filtered_df["Date"] <= end_date)
        ]


# -------------------------------------------------------------------
# 3. SUMMARY METRIC CARDS
# -------------------------------------------------------------------
st.subheader("📊 Overall Summary (Selected Countries & Date Range)")

# Use the latest date's cumulative numbers per country, then sum
latest_snapshot = (
    filtered_df.sort_values("Date")
    .groupby("Country")
    .tail(1)
)

total_cases = int(latest_snapshot["Confirmed"].sum())
total_deaths = int(latest_snapshot["Deaths"].sum())
total_recovered = int(latest_snapshot["Recovered"].sum())
total_vaccinated = int(latest_snapshot["Vaccinated"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("🟠 Total Cases", f"{total_cases:,}")
col2.metric("🟢 Total Recovered", f"{total_recovered:,}")
col3.metric("🔴 Total Deaths", f"{total_deaths:,}")
col4.metric("💉 Total Vaccinated", f"{total_vaccinated:,}")

st.markdown("---")


# -------------------------------------------------------------------
# 4. TREND OVER TIME (LINE CHARTS)
# -------------------------------------------------------------------
st.subheader("📈 Trend Over Time")

trend_metric = st.radio(
    "Choose metric to view trend for:",
    ["Confirmed", "Recovered", "Deaths", "Vaccinated"],
    horizontal=True
)

fig, ax = plt.subplots(figsize=(10, 5))

for country in selected_countries:
    country_data = filtered_df[filtered_df["Country"] == country].sort_values("Date")
    ax.plot(country_data["Date"], country_data[trend_metric], label=country, linewidth=2)

ax.set_xlabel("Date")
ax.set_ylabel(trend_metric)
ax.set_title(f"{trend_metric} Over Time")
ax.legend(loc="upper left", fontsize=8)
ax.grid(alpha=0.3)
fig.autofmt_xdate()

st.pyplot(fig)

st.markdown("---")


# -------------------------------------------------------------------
# 5. COUNTRY-WISE COMPARISON (BAR CHARTS)
# -------------------------------------------------------------------
st.subheader("🌍 Country-Wise Comparison (Latest Totals)")

comparison_df = latest_snapshot.set_index("Country")[
    ["Confirmed", "Recovered", "Deaths", "Vaccinated"]
]

col_left, col_right = st.columns(2)

with col_left:
    fig2, ax2 = plt.subplots(figsize=(6, 5))
    comparison_df[["Confirmed", "Recovered", "Deaths"]].plot(
        kind="bar", ax=ax2, color=["orange", "green", "red"]
    )
    ax2.set_title("Cases vs Recoveries vs Deaths")
    ax2.set_ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig2)

with col_right:
    fig3, ax3 = plt.subplots(figsize=(6, 5))
    comparison_df["Vaccinated"].plot(
        kind="bar", ax=ax3, color="steelblue"
    )
    ax3.set_title("Vaccinated Population by Country")
    ax3.set_ylabel("Vaccinated Count")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(fig3)

st.markdown("---")


# -------------------------------------------------------------------
# 6. RECOVERY & DEATH RATE (using numpy calculations)
# -------------------------------------------------------------------
st.subheader("🧮 Recovery Rate vs Death Rate (%)")

comparison_df["Recovery Rate (%)"] = np.round(
    (comparison_df["Recovered"] / comparison_df["Confirmed"]) * 100, 2
)
comparison_df["Death Rate (%)"] = np.round(
    (comparison_df["Deaths"] / comparison_df["Confirmed"]) * 100, 2
)

fig4, ax4 = plt.subplots(figsize=(10, 5))
comparison_df[["Recovery Rate (%)", "Death Rate (%)"]].plot(
    kind="bar", ax=ax4, color=["seagreen", "crimson"]
)
ax4.set_title("Recovery Rate vs Death Rate by Country")
ax4.set_ylabel("Percentage (%)")
plt.xticks(rotation=45, ha="right")
st.pyplot(fig4)

st.markdown("---")


# -------------------------------------------------------------------
# 7. RAW DATA TABLE (OPTIONAL VIEW)
# -------------------------------------------------------------------
with st.expander("🔍 View Raw Data Table"):
    st.dataframe(filtered_df.sort_values("Date", ascending=False))

st.caption("Built with Streamlit, Pandas, NumPy & Matplotlib")

st.subheader("🥧 Overall Distribution")

fig5, ax5 = plt.subplots(figsize=(6,6))

values = [
    total_cases,
    total_recovered,
    total_deaths
]

labels = [
    "Confirmed",
    "Recovered",
    "Deaths"
]

ax5.pie(
    values,
    labels=labels,
    autopct="%1.1f%%",
    startangle=90
)

ax5.set_title("COVID Distribution")
st.pyplot(fig5)

st.subheader("📍 Vaccination vs Confirmed Cases")

fig6, ax6 = plt.subplots(figsize=(8,5))

ax6.scatter(
    comparison_df["Confirmed"],
    comparison_df["Vaccinated"],
    s=120
)

for country in comparison_df.index:
    ax6.text(
        comparison_df.loc[country,"Confirmed"],
        comparison_df.loc[country,"Vaccinated"],
        country
    )

ax6.set_xlabel("Confirmed Cases")
ax6.set_ylabel("Vaccinated")
ax6.set_title("Vaccination vs Confirmed Cases")

st.pyplot(fig6)

st.subheader("🏆 Top 5 Countries")

top5 = comparison_df.sort_values(
    by="Confirmed",
    ascending=False
).head(5)

st.dataframe(top5)

st.subheader("📋 Summary Statistics")

st.write(filtered_df.describe())

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="COVID_Filtered_Data.csv",
    mime="text/csv"
)

report = f"""
COVID ANALYTICS REPORT

Total Cases : {total_cases:,}
Recovered   : {total_recovered:,}
Deaths      : {total_deaths:,}
Vaccinated  : {total_vaccinated:,}

Recovery Rate:
{comparison_df['Recovery Rate (%)']}

Death Rate:
{comparison_df['Death Rate (%)']}
"""

st.download_button(
    label="📄 Download Report",
    data=report,
    file_name="COVID_Report.txt",
    mime="text/plain"
)

