"""
Commute Emissions Calculator — Scope 3 Category 7
Formula: round_trip_distance_miles × days_onsite_per_week × 52 × mode_factor
Mode factors (kg CO2 per vehicle-mile or passenger-mile):
  Passenger Car: 0.297, Light Truck: 0.394, Motorcycle: 0.368
  Rail: 0.096, Bus: 0.066
"""
import pandas as pd
import numpy as np

MODE_FACTORS = {
    "car": 0.297, "passenger car": 0.297,
    "light truck": 0.394, "truck": 0.394, "suv": 0.394,
    "motorcycle": 0.368,
    "rail": 0.096, "train": 0.096, "subway": 0.093, "tram": 0.093, "transit": 0.093,
    "bus": 0.066,
    "walk": 0.0, "bike": 0.0, "bicycle": 0.0, "wfh": 0.0, "remote": 0.0,
}
DEFAULT_EF = 0.297

def load(filepath): return pd.read_csv(filepath)

def preprocess(df):
    df = df.copy()
    df["commute_mode"] = df["commute_mode"].str.lower().str.strip()
    df["vehicle_type"] = df["vehicle_type"].str.lower().str.strip()
    df["round_trip_distance_miles"] = pd.to_numeric(df["round_trip_distance_miles"], errors="coerce").fillna(0)
    df["days_onsite_per_week"] = pd.to_numeric(df["days_onsite_per_week"], errors="coerce").fillna(5)
    df["occupancy"] = pd.to_numeric(df["occupancy"], errors="coerce").fillna(1).clip(lower=1)
    df["invoice_amount_usd"] = pd.to_numeric(df["invoice_amount_usd"], errors="coerce").fillna(0)
    return df

def get_ef(mode):
    if pd.isna(mode): return DEFAULT_EF
    mode = str(mode).lower()
    for key, val in MODE_FACTORS.items():
        if key in mode: return val
    return DEFAULT_EF

def calculate_emissions(df):
    df = df.copy()
    df["mode_factor"] = df["commute_mode"].apply(get_ef)
    # Annual emissions per employee
    df["annual_miles"] = df["round_trip_distance_miles"] * df["days_onsite_per_week"] * 52
    df["co2_kg"] = (df["annual_miles"] * df["mode_factor"]) / df["occupancy"]
    df["co2_tonnes"] = df["co2_kg"] / 1000
    return df

def aggregate(df):
    agg = {}
    agg["total_co2_tonnes"] = df["co2_tonnes"].sum()
    agg["by_mode"] = df.groupby("commute_mode")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    agg["by_mode"]["pct"] = (agg["by_mode"]["co2_tonnes"] / agg["by_mode"]["co2_tonnes"].sum() * 100).round(1)
    agg["by_worksite"] = df.groupby("worksite_location")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    agg["by_vehicle"] = df.groupby("vehicle_type")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    df["route"] = df["home_zip_code"].astype(str) + " → " + df["worksite_location"]
    agg["by_zip_route"] = df.groupby("worksite_location").agg(employees=("employee_id","count"), co2_tonnes=("co2_tonnes","sum")).reset_index().sort_values("co2_tonnes", ascending=False)
    agg["n_employees"] = len(df)
    agg["avg_per_employee"] = df["co2_tonnes"].mean()
    return agg, df

def run(filepath):
    df = load(filepath)
    df = preprocess(df)
    df = calculate_emissions(df)
    agg, df = aggregate(df)
    return df, agg
