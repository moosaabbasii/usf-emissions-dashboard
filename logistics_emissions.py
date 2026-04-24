"""
Logistics Emissions Calculator — Scope 3 Category 4
(Upstream Transportation & Distribution)

Formula: Freight emissions = ton-miles × mode emission factor
Where:  ton-miles = shipment_weight (tons) × distance_traveled (miles)

Emission factors from EPA SmartWay (kg CO2e per ton-mile):
  - Truck:  0.161
  - Rail:   0.027
  - Air:    0.800
  - Ship:   0.040
  - Default/Unknown: 0.161 (truck default)
"""

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# EMISSION FACTORS (kg CO2e per ton-mile)
# Source: EPA SmartWay
# ─────────────────────────────────────────────
EMISSION_FACTORS = {
    "truck":   0.161,
    "rail":    0.027,
    "air":     0.800,
    "ship":    0.040,
    "sea":     0.040,
    "ocean":   0.040,
    "train":   0.027,
    "default": 0.161,   # fallback to truck
}

# Fuel emission factors (kg CO2 per gallon)
FUEL_FACTORS = {
    "diesel":   10.21,
    "gasoline": 8.89,
    "cng":      6.23,   # compressed natural gas
    "default":  10.21,  # fallback to diesel
}

# Grid electricity factor (kg CO2 per kWh) — US average
ELECTRICITY_FACTOR = 0.386


def load_logistics_data(filepath: str) -> pd.DataFrame:
    """Load the synthetic logistics CSV."""
    df = pd.read_csv(filepath)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and standardize columns."""
    df = df.copy()

    # Normalize text columns
    df["mode_of_transport"] = df["mode_of_transport"].str.lower().str.strip()
    df["fuel_type"] = df["fuel_type"].str.lower().str.strip()
    df["carrier_type"] = df["carrier_type"].str.lower().str.strip()

    # Parse delivery datetime
    df["delivery_datetime"] = pd.to_datetime(df["delivery_datetime"], errors="coerce")
    df["year"]  = df["delivery_datetime"].dt.year
    df["month"] = df["delivery_datetime"].dt.month
    df["month_label"] = df["delivery_datetime"].dt.strftime("%b %Y")

    # Convert shipment weight from lbs to tons
    df["weight_tons"] = pd.to_numeric(df["shipment_weight_lb"], errors="coerce") / 2000

    # Ensure numeric
    df["distance_traveled"]   = pd.to_numeric(df["distance_traveled"],   errors="coerce")
    df["fuel_consumed"]       = pd.to_numeric(df["fuel_consumed_gallons"],errors="coerce").fillna(0)
    df["electricity_kwh"]     = pd.to_numeric(df["electricity_kwh"],      errors="coerce").fillna(0)
    df["idle_time_minutes"]   = pd.to_numeric(df["idle_time_minutes"],     errors="coerce").fillna(0)

    return df


def calculate_emissions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate CO2e emissions per shipment using two methods:

    Method 1 — Activity-based (ton-miles × emission factor)
      Used when distance_traveled and shipment_weight are available.

    Method 2 — Fuel-based (fuel_consumed × fuel factor + electricity × grid factor)
      Used as supplement / cross-check.

    Final column: co2_kg (primary estimate)
    """
    df = df.copy()

    # ── Method 1: Ton-mile based ──────────────────────────────
    def get_mode_factor(mode):
        if pd.isna(mode):
            return EMISSION_FACTORS["default"]
        for key in EMISSION_FACTORS:
            if key in str(mode):
                return EMISSION_FACTORS[key]
        return EMISSION_FACTORS["default"]

    df["mode_factor"] = df["mode_of_transport"].apply(get_mode_factor)
    df["ton_miles"]   = df["weight_tons"] * df["distance_traveled"]
    df["co2_kg_tonmile"] = df["ton_miles"] * df["mode_factor"]

    # ── Method 2: Fuel based ──────────────────────────────────
    def get_fuel_factor(fuel):
        if pd.isna(fuel):
            return FUEL_FACTORS["default"]
        for key in FUEL_FACTORS:
            if key in str(fuel):
                return FUEL_FACTORS[key]
        return FUEL_FACTORS["default"]

    df["fuel_factor"] = df["fuel_type"].apply(get_fuel_factor)
    df["co2_kg_fuel"] = (
        df["fuel_consumed"] * df["fuel_factor"] +
        df["electricity_kwh"] * ELECTRICITY_FACTOR
    )

    # ── Primary estimate: use ton-mile if available, else fuel-based ──
    df["co2_kg"] = np.where(
        df["co2_kg_tonmile"].notna() & (df["co2_kg_tonmile"] > 0),
        df["co2_kg_tonmile"],
        df["co2_kg_fuel"]
    )

    # Convert to metric tons for dashboard display
    df["co2_tonnes"] = df["co2_kg"] / 1000

    return df


def aggregate_for_dashboard(df: pd.DataFrame) -> dict:
    """
    Return aggregated dataframes ready to plug into Streamlit dashboard.
    """
    results = {}

    # ── Total emissions ───────────────────────────────────────
    results["total_co2_tonnes"] = df["co2_tonnes"].sum()

    # ── By month ──────────────────────────────────────────────
    monthly = (
        df.groupby(["year", "month", "month_label"])["co2_tonnes"]
        .sum()
        .reset_index()
        .sort_values(["year", "month"])
    )
    results["monthly"] = monthly

    # ── By transport mode ─────────────────────────────────────
    by_mode = (
        df.groupby("mode_of_transport")["co2_tonnes"]
        .sum()
        .reset_index()
        .sort_values("co2_tonnes", ascending=False)
    )
    results["by_mode"] = by_mode

    # ── By carrier ────────────────────────────────────────────
    by_carrier = (
        df.groupby("carrier_name")["co2_tonnes"]
        .sum()
        .reset_index()
        .sort_values("co2_tonnes", ascending=False)
    )
    results["by_carrier"] = by_carrier

    # ── By carrier type (LTL / FTL) ───────────────────────────
    by_carrier_type = (
        df.groupby("carrier_type")["co2_tonnes"]
        .sum()
        .reset_index()
    )
    results["by_carrier_type"] = by_carrier_type

    # ── By supplier location ──────────────────────────────────
    by_supplier = (
        df.groupby("supplier_location")["co2_tonnes"]
        .sum()
        .reset_index()
        .sort_values("co2_tonnes", ascending=False)
    )
    results["by_supplier"] = by_supplier

    # ── Top 10 highest-emission shipments ─────────────────────
    top_shipments = (
        df[["trip_id", "supplier_location", "destination_facility",
            "mode_of_transport", "carrier_name", "co2_tonnes"]]
        .sort_values("co2_tonnes", ascending=False)
        .head(10)
    )
    results["top_shipments"] = top_shipments

    # ── Intensity metric: kg CO2 per $ spent ──────────────────
    df["emission_intensity"] = df["co2_kg"] / df["invoice_amount_usd"].replace(0, np.nan)
    results["avg_intensity_kg_per_usd"] = df["emission_intensity"].mean()

    return results


def run(filepath: str) -> tuple:
    """
    Full pipeline. Returns (processed_df, aggregated_results).
    """
    df = load_logistics_data(filepath)
    df = preprocess(df)
    df = calculate_emissions(df)
    agg = aggregate_for_dashboard(df)
    return df, agg


# ─────────────────────────────────────────────
# Quick sanity check (won't run in Streamlit)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        df, agg = run(sys.argv[1])
        print(f"\nTotal CO2: {agg['total_co2_tonnes']:.2f} tonnes")
        print(f"\nMonthly breakdown:\n{agg['monthly']}")
        print(f"\nBy transport mode:\n{agg['by_mode']}")
        print(f"\nTop shipments:\n{agg['top_shipments']}")
    else:
        print("Usage: python logistics_emissions.py <path_to_csv>")
