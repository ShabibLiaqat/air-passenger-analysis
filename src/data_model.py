"""Validate the historical source and separate economies from aggregate series."""

from pathlib import Path
import math

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INDICATOR = "IS.AIR.PSGR"


def prepare_data(observations: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    required = {"Country Name", "Country Code", "Indicator Code", "Year", "Value"}
    if not required.issubset(observations.columns):
        raise ValueError("Passenger data is missing required columns.")
    if not {"Country Code", "Region", "IncomeGroup"}.issubset(countries.columns):
        raise ValueError("Country metadata is missing required columns.")
    if observations.empty:
        raise ValueError("Passenger data is empty.")
    frame = observations.copy()
    frame["Year"] = pd.to_numeric(frame["Year"], errors="raise")
    frame["Value"] = pd.to_numeric(frame["Value"], errors="raise")
    if frame[["Country Code", "Year", "Value"]].isna().any().any():
        raise ValueError("Source contains missing keys or observations.")
    if not frame["Indicator Code"].eq(INDICATOR).all():
        raise ValueError("This dashboard requires the passenger indicator IS.AIR.PSGR.")
    if not frame["Year"].between(1900, 2100).all() or not frame["Year"].mod(1).eq(0).all():
        raise ValueError("Source contains invalid annual observation years.")
    if not frame["Value"].map(math.isfinite).all() or frame["Value"].lt(0).any():
        raise ValueError("Passenger values must be finite and nonnegative.")
    if frame.duplicated(["Country Code", "Year"]).any():
        raise ValueError("Duplicate economy-year observations would inflate totals.")
    frame["Year"] = frame["Year"].astype(int)
    frame = frame.merge(countries, on="Country Code", how="left", validate="many_to_one")
    frame["Region"] = frame["Region"].replace(r"^\s*$", pd.NA, regex=True)
    # World Bank regional/income aggregates have no economy Region metadata.
    frame["is_aggregate"] = frame["Region"].isna()
    frame["IncomeGroup"] = frame["IncomeGroup"].fillna("Unclassified")
    return frame


def load_data(root: Path = ROOT) -> pd.DataFrame:
    return prepare_data(pd.read_csv(root / "data/passengers.csv"), pd.read_csv(root / "data/countries.csv"))


def matched_year_change(frame: pd.DataFrame, year: int) -> tuple[float | None, int]:
    """Compare only economies reporting in both the selected and previous year."""
    current = frame.loc[frame["Year"].eq(year), ["Country Code", "Value"]]
    previous = frame.loc[frame["Year"].eq(year - 1), ["Country Code", "Value"]]
    matched = current.merge(previous, on="Country Code", suffixes=("_current", "_previous"), validate="one_to_one")
    baseline = matched["Value_previous"].sum()
    if matched.empty or baseline <= 0:
        return None, len(matched)
    return (matched["Value_current"].sum() / baseline - 1) * 100, len(matched)


if __name__ == "__main__":
    data = load_data()
    print(f"Validated {len(data):,} observations; {int(data.is_aggregate.sum()):,} aggregate observations excluded from analysis.")
