from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.data_model import load_data, matched_year_change

ROOT = Path(__file__).resolve().parent
PALETTE = ["#66d9ef", "#ffbc69", "#a49dff", "#6be0b3", "#fa8f9d", "#80b5ff", "#d8b6ff"]
st.set_page_config(page_title="Air Passenger Atlas", page_icon="✈", layout="wide")
st.markdown("""<style>
.stApp {background:#0a111b}
[data-testid="stSidebar"] {background:#0d1723;border-right:1px solid #243447}
[data-testid="stMetric"] {background:#111b29;border:1px solid #243447;border-radius:12px;padding:18px}
[data-testid="stPlotlyChart"] {background:#111b29;border:1px solid #243447;border-radius:12px;padding:8px}
h1,h2,h3 {letter-spacing:-.025em}
.eyebrow {color:#66d9ef;font-size:12px;letter-spacing:.15em}
.lede {color:#a2b3c6;max-width:880px;line-height:1.7}
</style>""", unsafe_allow_html=True)


@st.cache_data
def cached_data(observations_modified, countries_modified):
    return load_data()


def chart(fig, height=350):
    fig.update_layout(height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#a2b3c6"), margin=dict(l=12, r=28, t=25, b=15),
                      legend=dict(orientation="h", y=-.18),
                      xaxis=dict(gridcolor="#243447"), yaxis=dict(gridcolor="#243447"))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})


def compact(value):
    for divisor, suffix in [(1e9, "bn"), (1e6, "m"), (1e3, "k")]:
        if abs(value) >= divisor:
            return f"{value / divisor:,.2f}{suffix}"
    return f"{value:,.0f}"


data = cached_data((ROOT / "data/passengers.csv").stat().st_mtime, (ROOT / "data/countries.csv").stat().st_mtime)
economies = data.loc[~data["is_aggregate"]].copy()
years = sorted(economies["Year"].unique().tolist())
with st.sidebar:
    st.markdown("<div class='eyebrow'>EXPLORE THE RECORD</div>", unsafe_allow_html=True)
    st.caption(f"Historical snapshot · {min(years)}–{max(years)}")
    selected_year = st.selectbox("Comparison year", years, index=len(years) - 1)
    regions = sorted(economies["Region"].unique())
    selected_regions = st.multiselect("Regions", regions, default=regions)
    income_options = sorted(economies["IncomeGroup"].unique())
    selected_incomes = st.multiselect("Income groups", income_options, default=income_options)
    selected_countries = st.multiselect("Economies (optional)", sorted(economies["Country Name"].unique()))
    st.divider()
    st.markdown("**What does this measure?**")
    st.caption("Passengers carried by airlines registered in each economy, including domestic and international flights. These are passenger carriage counts, not unique people or airport footfall.")
    st.caption("Regional and income aggregates are excluded to avoid double-counting. Missing observations are not replaced with zero.")

st.markdown("<div class='eyebrow'>AVIATION · WORLD DEVELOPMENT INDICATORS</div>", unsafe_allow_html=True)
st.title("Air Passenger Atlas")
st.markdown("<p class='lede'>Explore five decades of airline passenger traffic: where registered carriers operate at scale, how reporting economies compare, and how volumes changed around 2020.</p>", unsafe_allow_html=True)
st.info(f"Historical Power BI dataset · {min(years)}–{max(years)} · World Bank / ICAO · indicator IS.AIR.PSGR. This published snapshot is not a live feed.")

filtered = economies.loc[economies["Region"].isin(selected_regions) & economies["IncomeGroup"].isin(selected_incomes)].copy()
if selected_countries:
    filtered = filtered.loc[filtered["Country Name"].isin(selected_countries)]
current = filtered.loc[filtered["Year"].eq(selected_year)]
if current.empty:
    st.warning("No reported observations match these filters and year. Select another year or widen the filters.")
    st.stop()

total = current["Value"].sum()
change, matched_count = matched_year_change(filtered, selected_year)
high_share = current.loc[current["IncomeGroup"].str.casefold().eq("high income"), "Value"].sum() / total * 100 if total else None
c1,c2,c3,c4 = st.columns(4)
c1.metric(f"Passengers carried · {selected_year}", compact(total), help="Sum across the selected reporting economies for one year. Aggregate series excluded.")
c2.metric("Reporting economies", f"{len(current):,}", help="Economies with a reported value in the selected year; reporting varies across years.")
c3.metric("Change vs previous year", f"{change:+.1f}%" if change is not None else "—", help=f"Same-economy comparison across {matched_count} economies reporting in both {selected_year-1} and {selected_year}.")
c4.metric("High-income traffic share", f"{high_share:.1f}%" if high_share is not None else "—", help="Share of reported traffic in the current selection. Income classifications come from the original metadata snapshot.")

left,right = st.columns([1.45,1])
with left:
    st.subheader("Five decades of reported traffic")
    annual = filtered.groupby("Year", as_index=False).agg(passengers=("Value","sum"), reporting_economies=("Country Code","nunique"))
    fig = px.line(annual, x="Year", y="passengers", hover_data=["reporting_economies"], labels={"passengers":"Passengers", "Year":"Year"})
    fig.update_traces(line_color=PALETTE[0], line_width=3)
    fig.add_vline(x=selected_year, line_dash="dot", line_color=PALETTE[1])
    fig.add_vrect(x0=2019.5, x1=2020.5, fillcolor=PALETTE[1], opacity=.08, line_width=0)
    chart(fig)
    st.caption("Reporting coverage varies by year. The highlighted band marks 2020; the dotted line marks your selected year.")
with right:
    st.subheader(f"Traffic by region · {selected_year}")
    by_region = current.groupby("Region", as_index=False)["Value"].sum().sort_values("Value")
    fig = px.bar(by_region, x="Value", y="Region", orientation="h", labels={"Value":"Passengers", "Region":""})
    fig.update_traces(marker_color=PALETTE[1])
    chart(fig)

left,right = st.columns([1.45,1])
with left:
    st.subheader(f"Leading reporting economies · {selected_year}")
    leaders = current.nlargest(12,"Value").sort_values("Value")
    fig = px.bar(leaders, x="Value", y="Country Name", orientation="h", color="Region", color_discrete_sequence=PALETTE, labels={"Value":"Passengers", "Country Name":""})
    fig.update_yaxes(categoryorder="array", categoryarray=leaders["Country Name"].tolist())
    fig.update_layout(showlegend=False)
    chart(fig,390)
with right:
    st.subheader("How traffic splits by income group")
    by_income = current.groupby("IncomeGroup",as_index=False)["Value"].sum()
    fig = px.pie(by_income,names="IncomeGroup",values="Value",hole=.65,color_discrete_sequence=PALETTE)
    fig.update_traces(textinfo="percent",textposition="inside")
    chart(fig,390)
    st.caption("Income groups are the classifications stored in the original report, applied across its historical series.")

with st.expander("Explore the underlying records"):
    table = current[["Country Name","Country Code","Region","IncomeGroup","Year","Value"]].sort_values("Value",ascending=False)
    st.dataframe(table,hide_index=True,width="stretch")
    st.download_button("Download this selection",table.to_csv(index=False).encode(),f"air_passengers_{selected_year}.csv","text/csv")
with st.expander("Methodology and coverage"):
    st.write(f"The source contains {len(data):,} country/aggregate-year observations. {int(data.is_aggregate.sum()):,} aggregate observations are excluded. Country totals use only records with economy-region metadata.")
    st.write(f"The year-over-year metric compares {matched_count} economies reporting in both adjacent years. Missing country-years are absent rather than zeros. Counts can include repeated journeys by the same passenger.")
    st.dataframe(annual[["Year","reporting_economies"]],hide_index=True,width="stretch")
    st.write("The original Power BI model and DAX measures are documented in the GitHub repository. This Streamlit adaptation adds aggregate exclusion and a matched-economy growth calculation.")
st.divider()
st.caption("Source: World Bank World Development Indicators / International Civil Aviation Organization. Historical snapshot extracted from the original Power BI report.")
st.markdown("[Indicator definition](https://data.worldbank.org/indicator/IS.AIR.PSGR) · [Source and methodology](https://databank.worldbank.org/metadataglossary/world-development-indicators/series/IS.AIR.PSGR)")
st.markdown('<span id="dashboard-ready" style="display:none"></span>',unsafe_allow_html=True)
