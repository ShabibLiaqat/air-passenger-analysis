# Portfolio case study: Air Passenger Atlas

## Business question

How did airline passenger carriage change across reporting economies around 2020, and how do regional and income-group volumes compare? Aviation activity is relevant to connectivity and business planning, but a useful comparison must distinguish country records from published aggregates and account for changing reporting coverage.

## Source analysis

The original Power BI report uses World Bank indicator IS.AIR.PSGR and covers 1970–2021. It contains 9,898 observations, country metadata, a passenger measure and three income-group measures. Its dashboard combines country comparisons, a trend chart, income-group shares and interactive slicers.

## What the web adaptation adds

The Streamlit version keeps the original indicator and observed values while exposing the analysis to viewers without Power BI Desktop. The data pipeline validates unique economy-year keys and excludes 2,269 aggregate observations from economy-level analysis. Headline cards show one selected year, and growth is calculated using only economies reporting in both adjacent years.

Those decisions matter: adding the World, region, and income-group series to national values would inflate the total, while comparing totals across changing country coverage can invent growth. Income classifications remain those captured in the original metadata, so historical comparisons are clearly described as using a fixed classification snapshot.

## Results

Across 149 economies reporting in both 2019 and 2020, passenger carriage contracted by 60.2%. Across 151 reporting in both 2020 and 2021, it increased by 28.7%. The 2021 country selection totals 2.28 billion passenger carriages across 155 economies, led by the United States and China.

The contraction and recovery describe the historical series; the chart highlights 2020 without claiming a causal model. The indicator measures carriage by airlines registered in each economy, rather than unique travellers, airport visitors, or cargo.

## Delivery

The GitHub repository includes source CSVs, the original DAX expressions and relationships, a data dictionary, calculation tests, an interactive app, and a dashboard preview. GitHub Actions validates the data, renders the app and updates the preview when the app or dataset changes. Streamlit Community Cloud can host the interactive application with no API credentials.

The original PBIX remains unchanged locally. The current portfolio is a historical analysis rather than an API-fed current market dashboard.
