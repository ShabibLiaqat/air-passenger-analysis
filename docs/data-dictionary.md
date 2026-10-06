# Historical aviation data and model

## Observation table: passengers.csv

| Field | Meaning |
| --- | --- |
| Country Name | Economy or published aggregate name |
| Country Code | World Bank economy/aggregate identifier |
| Indicator Name | Air transport, passengers carried |
| Indicator Code | IS.AIR.PSGR |
| Year | Annual observation year, 1970–2021 in this report |
| Value | Reported passenger carriage count; not unique people |

## Country metadata: countries.csv

`Country Code` joins each observation to `Region`, `IncomeGroup`, `SpecialNotes`, and `TableName` (the metadata economy name). Aggregate codes have no economy region in this snapshot. The Streamlit dashboard uses that distinction to exclude aggregates; missing metadata is conservatively excluded as well.

`indicator.csv` preserves the source definition and source organisation stored in the report. The report's automatic date template is not exported because the analysis uses annual observations directly.

## Measures and adaptation

The original DAX measures sum `Data[Value]`, with filters for high, low, and middle income groups. Their original expressions are preserved in `powerbi/Measures.dax`. Power BI text comparisons are case-insensitive; the web version normalises the high-income label's case when calculating its share.

The web version presents one selected year rather than summing passenger counts across every year in a headline card. It excludes overlapping aggregate records and calculates growth on matched economy codes. For that reason, its headline totals should not be expected to equal an unfiltered sum from the original report.

All years use the same stored income and region classifications. Reporting availability changes over time, and these historical data should not be treated as an exhaustive current aviation-market view.
