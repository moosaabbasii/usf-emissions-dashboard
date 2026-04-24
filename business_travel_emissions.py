"""
Business Travel Emissions Calculator — Scope 3 Category 6
Formula:
  Air:  passenger_distance × cabin/haul factor
        short-haul (<300mi): 0.207, medium (300-2300mi): 0.129, long (>=2300mi): 0.163
  Rail: passenger_distance × 0.096
  Road: miles × 0.297
  Bus:  passenger_distance × 0.066
"""
import pandas as pd
import numpy as np

AIR_SHORT  = 0.207
AIR_MEDIUM = 0.129
AIR_LONG   = 0.163
RAIL_EF    = 0.096
ROAD_EF    = 0.297
BUS_EF     = 0.066

def load(filepath): return pd.read_csv(filepath)

def preprocess(df):
    df = df.copy()
    df["travel_mode"] = df["travel_mode"].str.lower().str.strip()
    df["trip_start_date"] = pd.to_datetime(df["trip_start_date"], errors="coerce")
    df["year"]  = df["trip_start_date"].dt.year
    df["month"] = df["trip_start_date"].dt.month
    df["month_label"] = df["trip_start_date"].dt.strftime("%b %Y")
    df["distance_traveled"] = pd.to_numeric(df["distance_traveled"], errors="coerce").fillna(0)
    df["invoice_amount_usd"] = pd.to_numeric(df["invoice_amount_usd"], errors="coerce").fillna(0)
    return df

def calculate_emissions(df):
    df = df.copy()
    def ef(row):
        mode = str(row["travel_mode"])
        dist = row["distance_traveled"]
        if "air" in mode or "flight" in mode or "plane" in mode:
            if dist < 300:   return dist * AIR_SHORT
            elif dist < 2300: return dist * AIR_MEDIUM
            else:             return dist * AIR_LONG
        elif "rail" in mode or "train" in mode: return dist * RAIL_EF
        elif "bus" in mode:                     return dist * BUS_EF
        elif "car" in mode or "road" in mode or "taxi" in mode or "cab" in mode or "rental" in mode: return dist * ROAD_EF
        else: return dist * ROAD_EF  # default
    df["co2_kg"] = df.apply(ef, axis=1)
    df["co2_tonnes"] = df["co2_kg"] / 1000
    return df

def aggregate(df):
    agg = {}
    agg["total_co2_tonnes"] = df["co2_tonnes"].sum()
    agg["monthly"] = df.groupby(["year","month","month_label"])["co2_tonnes"].sum().reset_index().sort_values(["year","month"])
    agg["by_mode"] = df.groupby("travel_mode")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    agg["by_purpose"] = df.groupby("trip_purpose")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False)
    df["route"] = df["origin"] + " → " + df["destination"]
    agg["by_route"] = df.groupby("route")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes", ascending=False).head(15)
    agg["by_route"]["pct"] = (agg["by_route"]["co2_tonnes"] / agg["by_route"]["co2_tonnes"].sum() * 100).round(1)
    agg["cost_by_mode"] = df.groupby("travel_mode").agg(co2_tonnes=("co2_tonnes","sum"), invoice=("invoice_amount_usd","sum")).reset_index()
    agg["cost_by_mode"]["cost_per_tonne"] = (agg["cost_by_mode"]["invoice"] / agg["cost_by_mode"]["co2_tonnes"]).round(2)
    agg["avg_intensity"] = (df["co2_kg"].sum() / df["invoice_amount_usd"].replace(0,np.nan).sum())
    return agg, df

def run(filepath):
    df = load(filepath)
    df = preprocess(df)
    df = calculate_emissions(df)
    agg, df = aggregate(df)
    return df, agg
