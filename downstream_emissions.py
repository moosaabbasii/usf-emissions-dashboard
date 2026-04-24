"""
Downstream Transport Emissions Calculator — Scope 3 Category 9
Formula: shipment_weight_lb × distance_traveled × mode_factor
Mode factors (kg CO2 per short ton-mile):
  Road: 0.186, Rail: 0.021, Water: 0.077, Air: 1.086
"""
import pandas as pd
import numpy as np

MODE_FACTORS = {
    "road": 0.186, "truck": 0.186,
    "rail": 0.021, "train": 0.021,
    "water": 0.077, "sea": 0.077, "ocean": 0.077, "ship": 0.077,
    "air": 1.086, "plane": 1.086,
}
DEFAULT_EF = 0.186

FUEL_FACTORS = {"diesel": 10.21, "gasoline": 8.89, "cng": 6.23}
ELECTRICITY_EF = 0.386

def load(filepath): return pd.read_csv(filepath)

def preprocess(df):
    df = df.copy()
    df["mode_of_transport"] = df["mode_of_transport"].str.lower().str.strip()
    df["delivery_datetime"] = pd.to_datetime(df["delivery_datetime"], errors="coerce")
    df["year"]  = df["delivery_datetime"].dt.year
    df["month"] = df["delivery_datetime"].dt.month
    df["month_label"] = df["delivery_datetime"].dt.strftime("%b %Y")
    df["distance_traveled"] = pd.to_numeric(df["distance_traveled"], errors="coerce").fillna(0)
    df["shipment_weight_lb"] = pd.to_numeric(df["shipment_weight_lb"], errors="coerce").fillna(0)
    df["shipment_volume_cuft"] = pd.to_numeric(df["shipment_volume_cuft"] if "shipment_volume_cuft" in df.columns else df.get("shipment_volume_cuft", 0), errors="coerce").fillna(0)
    df["fuel_consumed_gallons"] = pd.to_numeric(df["fuel_consumed_gallons"], errors="coerce").fillna(0)
    df["electricity_kwh"] = pd.to_numeric(df["electricity_kwh"], errors="coerce").fillna(0)
    df["weight_short_tons"] = df["shipment_weight_lb"] / 2000
    return df

def get_ef(mode):
    if pd.isna(mode): return DEFAULT_EF
    for key, val in MODE_FACTORS.items():
        if key in str(mode): return val
    return DEFAULT_EF

def calculate_emissions(df):
    df = df.copy()
    df["mode_factor"] = df["mode_of_transport"].apply(get_ef)
    df["ton_miles"] = df["weight_short_tons"] * df["distance_traveled"]
    df["co2_kg"] = df["ton_miles"] * df["mode_factor"]
    df["co2_tonnes"] = df["co2_kg"] / 1000
    return df

def aggregate(df):
    agg = {}
    agg["total_co2_tonnes"] = df["co2_tonnes"].sum()
    agg["monthly"] = df.groupby(["year","month","month_label"])["co2_tonnes"].sum().reset_index().sort_values(["year","month"])
    agg["by_mode"] = df.groupby("mode_of_transport")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    df["route"] = df["origin"] + " → " + df["destination"]
    by_route = df.groupby("route")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False).head(15)
    by_route["pct"] = (by_route["co2_tonnes"] / by_route["co2_tonnes"].sum() * 100).round(1)
    agg["by_route"] = by_route
    agg["by_carrier"] = df.groupby("carrier_name")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    agg["by_carrier"]["pct"] = (agg["by_carrier"]["co2_tonnes"] / agg["by_carrier"]["co2_tonnes"].sum() * 100).round(1)

    # Volume bins
    vol_col = "shipment_volume_cuft" if "shipment_volume_cuft" in df.columns else None
    if vol_col:
        df["volume_bin"] = pd.qcut(df[vol_col], q=4, labels=["Small","Medium","Large","X-Large"], duplicates="drop")
        agg["by_volume"] = df.groupby("volume_bin", observed=True)["co2_tonnes"].sum().reset_index()

    # Weight bins
    df["weight_bin"] = pd.qcut(df["shipment_weight_lb"], q=4, labels=["Light","Medium","Heavy","X-Heavy"], duplicates="drop")
    agg["by_weight"] = df.groupby("weight_bin", observed=True)["co2_tonnes"].sum().reset_index()

    # Cost
    if "invoice_amount_usd" in df.columns:
        df["invoice_amount_usd"] = pd.to_numeric(df["invoice_amount_usd"], errors="coerce").fillna(0)
        agg["cost_by_mode"] = df.groupby("mode_of_transport").agg(co2_tonnes=("co2_tonnes","sum"), invoice=("invoice_amount_usd","sum")).reset_index()
        agg["cost_by_mode"]["cost_per_tonne"] = (agg["cost_by_mode"]["invoice"] / agg["cost_by_mode"]["co2_tonnes"]).round(2)
        agg["cost_by_mode"]["mode_of_transport"] = agg["cost_by_mode"]["mode_of_transport"].str.capitalize()

    return agg, df

def run(filepath):
    df = load(filepath)
    df = preprocess(df)
    df = calculate_emissions(df)
    agg, df = aggregate(df)
    return df, agg
