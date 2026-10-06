"""Rebuild the historical CSVs and model documentation from the original PBIX."""

import argparse
from pathlib import Path

from pbixray import PBIXRay
from src.data_model import ROOT, prepare_data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pbix", type=Path)
    args = parser.parse_args()
    model = PBIXRay(str(args.pbix))
    observations = model.get_table("Data")
    countries = model.get_table("Metadata - Countries")
    prepare_data(observations, countries)
    for table, filename in [("Data", "passengers.csv"), ("Metadata - Countries", "countries.csv"), ("Metadata - Indicators", "indicator.csv")]:
        model.get_table(table).to_csv(ROOT / "data" / filename, index=False)
    model.relationships.to_json(ROOT / "powerbi/relationships.json", orient="records", indent=2)
    measures = "\n\n".join(f"{row['Name']} =\n{row['Expression']}" for _, row in model.dax_measures.iterrows())
    (ROOT / "powerbi/Measures.dax").write_text(measures + "\n", encoding="utf-8")
    print(f"Extracted {len(observations):,} observations from the local report.")


if __name__ == "__main__":
    main()
