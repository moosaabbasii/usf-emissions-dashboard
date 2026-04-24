"""
EV Transport Emissions Calculator — Scope 3 (EV Fleet)
Emissions are pre-calculated in the dataset as total_emissions_kgco2
"""
import pandas as pd
import numpy as np

def load(filepath): return pd.read_csv(filepath)

def preprocess(df):
    df = df.copy()
    df["fuel_type_powertrain"] = df["fuel_type_powertrain"].str.lower().str.strip()
    df["vehicle_type_class_id"] = df["vehicle_type_class_id"].str.lower().str.strip() if df["vehicle_type_class_id"].dtype == object else df["vehicle_type_class_id"]
    df["trip_start_time"] = pd.to_datetime(df["trip_start_time"], errors="coerce")
    df["year"]  = df["trip_start_time"].dt.year
    df["month"] = df["trip_start_time"].dt.month
    df["month_label"] = df["trip_start_time"].dt.strftime("%b %Y")
    df["distance_traveled"]      = pd.to_numeric(df["distance_traveled"],      errors="coerce").fillna(0)
    df["total_emissions_kgco2"]  = pd.to_numeric(df["total_emissions_kgco2"],  errors="coerce").fillna(0)
    df["electricity_kwh"]        = pd.to_numeric(df["electricity_kwh"],        errors="coerce").fillna(0)
    df["fuel_quantity_gallons"]  = pd.to_numeric(df["fuel_quantity_gallons"],  errors="coerce").fillna(0)
    df["passenger_count"]        = pd.to_numeric(df["passenger_count"],        errors="coerce").fillna(1)
    df["idle_time_minutes"]      = pd.to_numeric(df["idle_time_minutes"],       errors="coerce").fillna(0)
    df["co2_kg"]     = df["total_emissions_kgco2"]
    df["co2_tonnes"] = df["co2_kg"] / 1000
    df["route"] = df["origin"] + " → " + df["destination"]
    return df

def aggregate(df):
    agg = {}
    agg["total_co2_tonnes"] = df["co2_tonnes"].sum()
    agg["total_miles"]      = df["distance_traveled"].sum()
    agg["n_trips"]          = len(df)

    # By vehicle type
    by_vt = df.groupby("vehicle_type_class_id").agg(
        co2_tonnes=("co2_tonnes","sum"),
        miles=("distance_traveled","sum"),
        trips=("vehicle_id","count")
    ).reset_index()
    by_vt["emissions_per_mile"] = (by_vt["co2_tonnes"]*1000 / by_vt["miles"].replace(0,np.nan)).round(4)
    by_vt = by_vt.sort_values("co2_tonnes", ascending=False)
    agg["by_vehicle_type"] = by_vt

    # By powertrain
    by_pt = df.groupby("fuel_type_powertrain").agg(
        co2_tonnes=("co2_tonnes","sum"),
        miles=("distance_traveled","sum"),
        trips=("vehicle_id","count")
    ).reset_index()
    by_pt["emissions_per_mile"] = (by_pt["co2_tonnes"]*1000 / by_pt["miles"].replace(0,np.nan)).round(4)
    by_pt = by_pt.sort_values("co2_tonnes", ascending=False)
    agg["by_powertrain"] = by_pt

    # Monthly
    agg["monthly"] = df.groupby(["year","month","month_label"])["co2_tonnes"].sum().reset_index().sort_values(["year","month"])

    # By route (frequency + emissions)
    by_route = df.groupby("route").agg(
        trips=("vehicle_id","count"),
        co2_tonnes=("co2_tonnes","sum"),
        miles=("distance_traveled","sum")
    ).reset_index().sort_values("co2_tonnes", ascending=False).head(15)
    by_route["pct"] = (by_route["co2_tonnes"] / by_route["co2_tonnes"].sum() * 100).round(1)
    agg["by_route"] = by_route

    return agg, df

def run(filepath):
    df = load(filepath)
    df = preprocess(df)
    agg, df = aggregate(df)
    return df, agg
