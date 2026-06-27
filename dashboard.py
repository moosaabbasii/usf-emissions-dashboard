"""
GHG Emissions Dashboard — Scope 3 Full Dashboard
USF / Patel's College — Global Sustainability Research
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from logistics_emissions import run as run_logistics
from business_travel_emissions import run as run_business
from commute_emissions import run as run_commute
from downstream_emissions import run as run_downstream
from ev_emissions import run as run_ev
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

st.set_page_config(page_title="Emissions Dashboard", page_icon="🌍", layout="wide")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"],[data-testid="stApp"]{background-color:#0f1117;}
    .main .block-container{padding:2rem 2.5rem;max-width:100%;background-color:#0f1117;}
    .kpi-card{background:#1e2130;border-radius:12px;padding:1.2rem 1.5rem;border-left:4px solid;margin-bottom:0.5rem;}
    .kpi-label{font-size:.75rem;color:#9ca3af;font-weight:600;text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px;}
    .kpi-value{font-size:2rem;font-weight:700;color:#f9fafb;line-height:1.1;}
    .kpi-sub{font-size:.80rem;color:#6b7280;margin-top:4px;}
    .section-title{font-size:1rem;font-weight:700;color:#f3f4f6;margin-bottom:.75rem;margin-top:1.5rem;}
    .insight-box{background:#1e2130;border:1px solid #374151;border-radius:8px;padding:.9rem 1.1rem;margin-top:1rem;font-size:.85rem;color:#9ca3af;line-height:1.6;}
    hr{border-color:#374151;}
</style>
""", unsafe_allow_html=True)

BG="#1e2130"; GRID="#2d3348"; TEXT="#e5e7eb"; SUBTEXT="#9ca3af"
COLORS=["#10b981","#3b82f6","#f59e0b","#8b5cf6","#ef4444","#06b6d4","#f97316"]

CHART_LAYOUT=dict(
    paper_bgcolor=BG,plot_bgcolor=BG,
    font=dict(family="Inter, sans-serif",color=TEXT,size=12),
    margin=dict(t=50,b=40,l=50,r=20),
    title_font=dict(color=TEXT,size=14),
    legend=dict(font=dict(color=TEXT,size=11),bgcolor="rgba(0,0,0,0)",bordercolor="rgba(0,0,0,0)"),
    xaxis=dict(gridcolor=GRID,linecolor=GRID,tickcolor=SUBTEXT,tickfont=dict(color=SUBTEXT),title_font=dict(color=SUBTEXT),showgrid=True,zeroline=False),
    yaxis=dict(gridcolor=GRID,linecolor=GRID,tickcolor=SUBTEXT,tickfont=dict(color=SUBTEXT),title_font=dict(color=SUBTEXT),showgrid=True,zeroline=False),
)

def T(fig,title=""):
    fig.update_layout(**CHART_LAYOUT)
    if title: fig.update_layout(title_text=title)
    return fig

def pie(fig):
    fig.update_layout(**CHART_LAYOUT)
    fig.update_layout(xaxis=dict(visible=False),yaxis=dict(visible=False))
    return fig

def kpi(label,value,sub,color):
    return f'<div class="kpi-card" style="border-color:{color}"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-sub">{sub}</div></div>'

# ── FILE PATHS ────────────────────────────────
PATHS = {
    "logistics":  "synthetic_logistics_emissions_data.csv",
    "business":   "synthetic_business_travel_data_v2.csv",
    "commute":    "synthetic_commute_data_v2.csv",
    "downstream": "synthetic_downstream_transport_data_v2.csv",
    "ev":         "synthetic_ev_transport_data_with_emissions.csv",
}

# ── SIDEBAR ───────────────────────────────────
with st.sidebar:
    st.markdown("## 🌍 Emissions Dashboard")
    st.markdown("---")
    page = st.radio("", [
        "Overview",
        "Scope 3 — Cat 4: Logistics",
        "Scope 3 — Cat 6: Business Travel",
        "Scope 3 — Cat 7: Commute",
        "Scope 3 — Cat 9: Downstream Transport",
        "Scope 1 — EV Transport",
        "🤖 ML — Anomaly Detection",
    ], label_visibility="collapsed")
    st.markdown("---")
    st.caption("USF / Patel's College\nGlobal Sustainability Research\nGHG Protocol (WRI/WBCSD)")

# ── LOAD DATA ─────────────────────────────────
@st.cache_data
def load_all():
    results = {}
    errors  = {}
    loaders = {
        "logistics":  (run_logistics,  PATHS["logistics"]),
        "business":   (run_business,   PATHS["business"]),
        "commute":    (run_commute,    PATHS["commute"]),
        "downstream": (run_downstream, PATHS["downstream"]),
        "ev":         (run_ev,         PATHS["ev"]),
    }
    for key, (fn, path) in loaders.items():
        try:
            df, agg = fn(path)
            results[key] = (df, agg)
        except Exception as e:
            errors[key] = str(e)
    return results, errors

data, errors = load_all()

def get(key):
    if key in data: return data[key]
    return None, None

# ══════════════════════════════════════════════
# OVERVIEW PAGE
# ══════════════════════════════════════════════
if page == "Overview":
    st.markdown("# Emissions Analysis Dashboard")
    st.markdown("*Scope 3 GHG emissions — GHG Protocol framework*")

    # Collect totals
    totals = {}
    for key in ["logistics","business","commute","downstream","ev"]:
        df, agg = get(key)
        totals[key] = agg["total_co2_tonnes"] if agg else 0

    grand_total = sum(totals.values())

    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi("Grand Total",f"{grand_total:,.0f}","kg CO₂","#10b981"),unsafe_allow_html=True)
    with c2: st.markdown(kpi("Cat 4 Logistics",f"{totals['logistics']:,.0f}","kg CO₂","#3b82f6"),unsafe_allow_html=True)
    with c3: st.markdown(kpi("Cat 6 Business Travel",f"{totals['business']:,.0f}","kg CO₂","#f59e0b"),unsafe_allow_html=True)
    c4,c5,c6 = st.columns(3)
    with c4: st.markdown(kpi("Cat 7 Commute",f"{totals['commute']:,.0f}","kg CO₂","#8b5cf6"),unsafe_allow_html=True)
    with c5: st.markdown(kpi("Cat 9 Downstream",f"{totals['downstream']:,.0f}","kg CO₂","#ef4444"),unsafe_allow_html=True)
    with c6: st.markdown(kpi("Scope 1 — EV Transport",f"{totals['ev']:,.0f}","kg CO₂","#06b6d4"),unsafe_allow_html=True)

    st.markdown("---")

    # Scope breakdown donut
    CAT_COLORS = {
        "Cat 4 Logistics":     "#3b82f6",
        "Cat 6 Business Travel":"#f59e0b",
        "Cat 7 Commute":       "#8b5cf6",
        "Cat 9 Downstream":    "#ef4444",
        "Scope 1 — EV Transport": "#06b6d4",
    }
    scope_df = pd.DataFrame({
        "Category": list(CAT_COLORS.keys()),
        "CO2_tonnes": [totals["logistics"],totals["business"],totals["commute"],totals["downstream"],totals["ev"]]
    })
    col1,col2 = st.columns(2)
    with col1:
        fig = px.pie(scope_df,values="CO2_tonnes",names="Category",hole=0.45,
                     color="Category",color_discrete_map=CAT_COLORS)
        fig.update_traces(textfont_color="#f9fafb",textfont_size=12,marker_line_color=BG,marker_line_width=2)
        fig = pie(fig); fig.update_layout(title_text="Scope 3 Emissions by Category")
        st.plotly_chart(fig,use_container_width=True)
    with col2:
        fig2 = px.bar(scope_df.sort_values("CO2_tonnes"),x="CO2_tonnes",y="Category",orientation="h",
                      color="Category",color_discrete_map=CAT_COLORS,
                      labels={"CO2_tonnes":"kg CO₂","Category":""})
        fig2.update_traces(showlegend=False)
        fig2 = T(fig2,"Emissions by Scope 3 Category")
        st.plotly_chart(fig2,use_container_width=True)

    if errors:
        st.markdown("---")
        for k,v in errors.items():
            st.warning(f"Could not load {k}: {v}")

# ══════════════════════════════════════════════
# LOGISTICS PAGE
# ══════════════════════════════════════════════
elif page == "Scope 3 — Cat 4: Logistics":
    df,agg = get("logistics")
    st.markdown("# Scope 3 — Category 4: Upstream Transportation & Distribution")
    st.markdown("*Freight emissions = ton-miles × mode emission factor (EPA SmartWay)*")
    if df is None: st.error(errors.get("logistics","Unknown error")); st.stop()

    monthly_raw = agg["monthly"].copy()
    month_counts = df.groupby(["year","month"])["trip_id"].count().reset_index()
    month_counts.columns=["year","month","count"]
    avg_c = month_counts["count"].mean()
    monthly_clean = monthly_raw.merge(month_counts,on=["year","month"])
    monthly_clean = monthly_clean[monthly_clean["count"]>=avg_c*0.5]

    st.markdown("### Filters")
    fc1,fc2,fc3=st.columns(3)
    with fc1: sel_mode=st.selectbox("Transport Mode",["All"]+sorted(df["mode_of_transport"].dropna().unique().tolist()))
    with fc2: sel_ct=st.selectbox("Carrier Type",["All"]+sorted(df["carrier_type"].dropna().unique().tolist()))
    with fc3: sel_sup=st.selectbox("Supplier",["All"]+sorted(df["supplier_location"].dropna().unique().tolist()))
    fdf=df.copy()
    if sel_mode!="All": fdf=fdf[fdf["mode_of_transport"]==sel_mode]
    if sel_ct!="All":   fdf=fdf[fdf["carrier_type"]==sel_ct]
    if sel_sup!="All":  fdf=fdf[fdf["supplier_location"]==sel_sup]
    fdf["route"]=fdf["supplier_location"]+" → "+fdf["destination_facility"]
    st.markdown("---")

    k1,k2,k3,k4=st.columns(4)
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.0f} kg CO₂")
    with k2: st.metric("Shipments",f"{len(fdf):,}")
    with k3: st.metric("Avg Distance",f"{fdf['distance_traveled'].mean():,.0f} miles")
    with k4: st.metric("Total Invoice",f"${fdf['invoice_amount_usd'].sum():,.0f}")
    st.markdown("---")

    # 1. Mode
    st.markdown('<div class="section-title">1. Emissions by Mode of Transport</div>',unsafe_allow_html=True)
    bm=fdf.groupby("mode_of_transport")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bm["mode_of_transport"]=bm["mode_of_transport"].str.capitalize()
    f1=px.bar(bm,x="mode_of_transport",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,
              text="co2_tonnes",labels={"mode_of_transport":"Mode","co2_tonnes":"kg CO₂"})
    f1.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
    st.plotly_chart(T(f1,"Emissions by Mode of Transport"),use_container_width=True)
    st.markdown("---")

    # 2. Shipment Volume
    st.markdown('<div class="section-title">2. Emissions by Shipment Volume</div>',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        fdf2=fdf.copy()
        fdf2["volume_bin"]=pd.qcut(fdf2["shipment_volume_ctf"],q=4,labels=["Small","Medium","Large","X-Large"],duplicates="drop")
        vagg=fdf2.groupby("volume_bin",observed=True)["co2_tonnes"].sum().reset_index()
        f2=px.bar(vagg,x="volume_bin",y="co2_tonnes",color="volume_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"volume_bin":"Volume Quartile","co2_tonnes":"kg CO₂"})
        f2.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f2,"Emissions by Volume Quartile"),use_container_width=True)
    with col2:
        f2b=px.scatter(fdf,x="shipment_volume_ctf",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,labels={"shipment_volume_ctf":"Volume (cu ft)","co2_tonnes":"kg CO₂","mode_of_transport":"Mode"})
        st.plotly_chart(T(f2b,"Volume vs Emissions by Mode"),use_container_width=True)
    st.markdown("---")

    # 3. Carrier
    st.markdown('<div class="section-title">3. Emissions by Carrier (% share)</div>',unsafe_allow_html=True)
    bc=fdf.groupby("carrier_name")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bc["pct"]=(bc["co2_tonnes"]/bc["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns(2)
    with col1:
        f3=px.pie(bc,values="co2_tonnes",names="carrier_name",color_discrete_sequence=COLORS,hole=0.4)
        f3.update_traces(textfont_color="#f9fafb",textfont_size=11,marker_line_color=BG,marker_line_width=2)
        f3=pie(f3); f3.update_layout(title_text="% of Emissions by Carrier")
        st.plotly_chart(f3,use_container_width=True)
    with col2:
        f3b=px.bar(bc.head(10),x="co2_tonnes",y="carrier_name",orientation="h",text="pct",
                   color="co2_tonnes",color_continuous_scale=[[0,"#1e3a5f"],[1,"#3b82f6"]],labels={"co2_tonnes":"kg CO₂","carrier_name":""})
        f3b.update_traces(texttemplate="%{text}%",textposition="outside",textfont_color=TEXT)
        f3b.update_layout(coloraxis_showscale=False)
        st.plotly_chart(T(f3b,"Top Carriers by Emissions"),use_container_width=True)
    st.markdown("---")

    # 4. Routes
    st.markdown('<div class="section-title">4. Emissions by Origin → Destination Pattern</div>',unsafe_allow_html=True)
    br=fdf.groupby("route")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False).head(15)
    br["pct"]=(br["co2_tonnes"]/br["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns([3,2])
    with col1:
        f4=px.bar(br,x="co2_tonnes",y="route",orientation="h",text="pct",color="co2_tonnes",
                  color_continuous_scale=[[0,"#064e3b"],[1,"#10b981"]],labels={"co2_tonnes":"kg CO₂","route":""})
        f4.update_traces(texttemplate="%{text}%",textposition="outside",textfont_color=TEXT)
        f4.update_layout(coloraxis_showscale=False,height=500)
        st.plotly_chart(T(f4,"Top 15 Routes by Emissions"),use_container_width=True)
    with col2:
        rt=fdf.groupby("route").agg(shipments=("trip_id","count"),co2_tonnes=("co2_tonnes","sum")).reset_index().sort_values("co2_tonnes",ascending=False).head(15)
        rt["co2_tonnes"]=rt["co2_tonnes"].round(2); rt.columns=["Route","Shipments","CO₂ (t)"]
        st.markdown('<div class="section-title" style="margin-top:.5rem">Route Summary</div>',unsafe_allow_html=True)
        st.dataframe(rt,use_container_width=True,hide_index=True,height=490)
    st.markdown("---")

    # 5. Cost
    st.markdown('<div class="section-title">5. Cost Analysis (Invoice)</div>',unsafe_allow_html=True)
    cm=fdf.groupby("mode_of_transport").agg(co2_tonnes=("co2_tonnes","sum"),invoice=("invoice_amount_usd","sum")).reset_index()
    cm["cost_per_tonne"]=(cm["invoice"]/cm["co2_tonnes"]).round(2)
    cm["mode_of_transport"]=cm["mode_of_transport"].str.capitalize()
    col1,col2=st.columns(2)
    with col1:
        f5=px.bar(cm,x="mode_of_transport",y="invoice",color="mode_of_transport",color_discrete_sequence=COLORS,text="invoice",labels={"mode_of_transport":"Mode","invoice":"Invoice ($)"})
        f5.update_traces(texttemplate="$%{text:,.0f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f5,"Invoice by Transport Mode"),use_container_width=True)
    with col2:
        f5b=px.scatter(fdf,x="invoice_amount_usd",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={"invoice_amount_usd":"Invoice ($)","co2_tonnes":"kg CO₂","mode_of_transport":"Mode"})
        st.plotly_chart(T(f5b,"Invoice vs Emissions"),use_container_width=True)
    cd=cm[["mode_of_transport","invoice","co2_tonnes","cost_per_tonne"]].copy()
    cd.columns=["Mode","Total Invoice ($)","CO₂ (t)","$/tonne CO₂e"]
    cd["Total Invoice ($)"]=cd["Total Invoice ($)"].round(0); cd["CO₂ (t)"]=cd["CO₂ (t)"].round(2)
    st.dataframe(cd,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════
# BUSINESS TRAVEL PAGE
# ══════════════════════════════════════════════
elif page == "Scope 3 — Cat 6: Business Travel":
    df,agg = get("business")
    st.markdown("# Scope 3 — Category 6: Business Travel")
    st.markdown("*Air: passenger-distance × haul factor | Road: miles × 0.297 | Rail: passenger-distance × 0.096*")
    if df is None: st.error(errors.get("business","Unknown error")); st.stop()

    st.markdown("### Filters")
    fc1,fc2,fc3=st.columns(3)
    with fc1: sel_m=st.selectbox("Travel Mode",["All"]+sorted(df["travel_mode"].dropna().unique().tolist()))
    with fc2: sel_p=st.selectbox("Trip Purpose",["All"]+sorted(df["trip_purpose"].dropna().unique().tolist()))
    with fc3: sel_d=st.selectbox("Department",["All"]+sorted(df["department"].dropna().unique().tolist()))
    fdf=df.copy()
    if sel_m!="All": fdf=fdf[fdf["travel_mode"]==sel_m]
    if sel_p!="All": fdf=fdf[fdf["trip_purpose"]==sel_p]
    if sel_d!="All": fdf=fdf[fdf["department"]==sel_d]
    fdf["route"]=fdf["origin"]+" → "+fdf["destination"]
    st.markdown("---")

    k1,k2,k3,k4=st.columns(4)
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.0f} kg CO₂")
    with k2: st.metric("Trips",f"{len(fdf):,}")
    with k3: st.metric("Avg Distance",f"{fdf['distance_traveled'].mean():,.0f} miles")
    with k4: st.metric("Total Invoice",f"${fdf['invoice_amount_usd'].sum():,.0f}")
    st.markdown("---")

    # 1. Mode
    st.markdown('<div class="section-title">1. Emissions by Mode of Travel</div>',unsafe_allow_html=True)
    bm=fdf.groupby("travel_mode")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bm["pct"]=(bm["co2_tonnes"]/bm["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns(2)
    with col1:
        f1=px.bar(bm,x="travel_mode",y="co2_tonnes",color="travel_mode",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"travel_mode":"Mode","co2_tonnes":"kg CO₂"})
        f1.update_traces(texttemplate="%{text:,.2f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f1,"Emissions by Travel Mode"),use_container_width=True)
    with col2:
        f1b=px.pie(bm,values="co2_tonnes",names="travel_mode",color_discrete_sequence=COLORS,hole=0.4)
        f1b.update_traces(textfont_color="#f9fafb",textfont_size=12,marker_line_color=BG,marker_line_width=2)
        f1b=pie(f1b); f1b.update_layout(title_text="% Share by Travel Mode")
        st.plotly_chart(f1b,use_container_width=True)
    st.markdown("---")

    # 2. Trip Purpose
    st.markdown('<div class="section-title">2. Emissions by Trip Purpose</div>',unsafe_allow_html=True)
    bp=fdf.groupby("trip_purpose")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bp["pct"]=(bp["co2_tonnes"]/bp["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns(2)
    with col1:
        f2=px.bar(bp,x="trip_purpose",y="co2_tonnes",color="trip_purpose",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"trip_purpose":"Purpose","co2_tonnes":"kg CO₂"})
        f2.update_traces(texttemplate="%{text:,.2f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f2,"Emissions by Trip Purpose"),use_container_width=True)
    with col2:
        f2b=px.pie(bp,values="co2_tonnes",names="trip_purpose",color_discrete_sequence=COLORS,hole=0.4)
        f2b.update_traces(textfont_color="#f9fafb",textfont_size=12,marker_line_color=BG,marker_line_width=2)
        f2b=pie(f2b); f2b.update_layout(title_text="% Share by Trip Purpose")
        st.plotly_chart(f2b,use_container_width=True)
    st.markdown("---")

    # 3. Routes
    st.markdown('<div class="section-title">3. Emissions by Origin → Destination Pattern</div>',unsafe_allow_html=True)
    br=fdf.groupby("route")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False).head(15)
    br["pct"]=(br["co2_tonnes"]/br["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns([3,2])
    with col1:
        f3=px.bar(br,x="co2_tonnes",y="route",orientation="h",text="pct",color="co2_tonnes",
                  color_continuous_scale=[[0,"#1e3a5f"],[1,"#f59e0b"]],labels={"co2_tonnes":"kg CO₂","route":""})
        f3.update_traces(texttemplate="%{text}%",textposition="outside",textfont_color=TEXT)
        f3.update_layout(coloraxis_showscale=False,height=500)
        st.plotly_chart(T(f3,"Top 15 Routes by Emissions"),use_container_width=True)
    with col2:
        rt=fdf.groupby("route").agg(trips=("employee_id","count"),co2_tonnes=("co2_tonnes","sum")).reset_index().sort_values("co2_tonnes",ascending=False).head(15)
        rt["co2_tonnes"]=rt["co2_tonnes"].round(3); rt.columns=["Route","Trips","CO₂ (t)"]
        st.markdown('<div class="section-title" style="margin-top:.5rem">Route Summary</div>',unsafe_allow_html=True)
        st.dataframe(rt,use_container_width=True,hide_index=True,height=490)
    st.markdown("---")

    # 4. Cost
    st.markdown('<div class="section-title">4. Cost Analysis (Invoice)</div>',unsafe_allow_html=True)
    cm=fdf.groupby("travel_mode").agg(co2_tonnes=("co2_tonnes","sum"),invoice=("invoice_amount_usd","sum")).reset_index()
    cm["cost_per_tonne"]=(cm["invoice"]/cm["co2_tonnes"]).round(2)
    col1,col2=st.columns(2)
    with col1:
        f4=px.bar(cm,x="travel_mode",y="invoice",color="travel_mode",color_discrete_sequence=COLORS,text="invoice",labels={"travel_mode":"Mode","invoice":"Invoice ($)"})
        f4.update_traces(texttemplate="$%{text:,.0f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f4,"Invoice by Travel Mode"),use_container_width=True)
    with col2:
        f4b=px.scatter(fdf,x="invoice_amount_usd",y="co2_tonnes",color="travel_mode",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={"invoice_amount_usd":"Invoice ($)","co2_tonnes":"kg CO₂","travel_mode":"Mode"})
        st.plotly_chart(T(f4b,"Invoice vs Emissions"),use_container_width=True)
    cd=cm[["travel_mode","invoice","co2_tonnes","cost_per_tonne"]].copy()
    cd.columns=["Mode","Total Invoice ($)","CO₂ (t)","$/tonne CO₂e"]
    cd["Total Invoice ($)"]=cd["Total Invoice ($)"].round(0); cd["CO₂ (t)"]=cd["CO₂ (t)"].round(3)
    st.dataframe(cd,use_container_width=True,hide_index=True)

# ══════════════════════════════════════════════
# COMMUTE PAGE
# ══════════════════════════════════════════════
elif page == "Scope 3 — Cat 7: Commute":
    df,agg = get("commute")
    st.markdown("# Scope 3 — Category 7: Employee Commuting")
    st.markdown("*Emissions = round-trip distance × days onsite/week × 52 weeks × mode factor*")
    if df is None: st.error(errors.get("commute","Unknown error")); st.stop()

    st.markdown("### Filters")
    fc1,fc2=st.columns(2)
    with fc1: sel_m=st.selectbox("Commute Mode",["All"]+sorted(df["commute_mode"].dropna().unique().tolist()))
    with fc2: sel_w=st.selectbox("Worksite",["All"]+sorted(df["worksite_location"].dropna().unique().tolist()))
    fdf=df.copy()
    if sel_m!="All": fdf=fdf[fdf["commute_mode"]==sel_m]
    if sel_w!="All": fdf=fdf[fdf["worksite_location"]==sel_w]
    st.markdown("---")

    k1,k2,k3,k4=st.columns(4)
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.0f} kg CO₂")
    with k2: st.metric("Employees",f"{len(fdf):,}")
    with k3: st.metric("Avg per Employee",f"{fdf['co2_tonnes'].mean():,.0f} kg CO₂")
    with k4: st.metric("Avg Round Trip",f"{fdf['round_trip_distance_miles'].mean():,.1f} miles")
    st.markdown("---")

    # 1. Commute Mode
    st.markdown('<div class="section-title">1. Emissions by Commute Mode (% of employees per mode)</div>',unsafe_allow_html=True)
    bm=fdf.groupby("commute_mode").agg(employees=("employee_id","count"),co2_tonnes=("co2_tonnes","sum")).reset_index()
    bm["pct_employees"]=(bm["employees"]/bm["employees"].sum()*100).round(1)
    bm["pct_emissions"]=(bm["co2_tonnes"]/bm["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns(2)
    with col1:
        f1=px.pie(bm,values="employees",names="commute_mode",color_discrete_sequence=COLORS,hole=0.4)
        f1.update_traces(textfont_color="#f9fafb",textfont_size=12,marker_line_color=BG,marker_line_width=2)
        f1=pie(f1); f1.update_layout(title_text="% Employees by Commute Mode")
        st.plotly_chart(f1,use_container_width=True)
    with col2:
        f1b=px.bar(bm.sort_values("co2_tonnes",ascending=False),x="commute_mode",y="co2_tonnes",
                   color="commute_mode",color_discrete_sequence=COLORS,text="co2_tonnes",
                   labels={"commute_mode":"Mode","co2_tonnes":"kg CO₂"})
        f1b.update_traces(texttemplate="%{text:,.2f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f1b,"Total Emissions by Commute Mode"),use_container_width=True)
    st.dataframe(bm.rename(columns={"commute_mode":"Mode","employees":"# Employees","co2_tonnes":"CO₂ (t)","pct_employees":"% Employees","pct_emissions":"% Emissions"}),use_container_width=True,hide_index=True)
    st.markdown("---")

    # 2. Worksite
    st.markdown('<div class="section-title">2. Emissions by Zip Code → Worksite Location</div>',unsafe_allow_html=True)
    bw=fdf.groupby("worksite_location").agg(employees=("employee_id","count"),co2_tonnes=("co2_tonnes","sum"),avg_dist=("round_trip_distance_miles","mean")).reset_index().sort_values("co2_tonnes",ascending=False)
    col1,col2=st.columns(2)
    with col1:
        f2=px.bar(bw,x="co2_tonnes",y="worksite_location",orientation="h",
                  color="co2_tonnes",color_continuous_scale=[[0,"#3b1a8b"],[1,"#8b5cf6"]],
                  text="employees",labels={"co2_tonnes":"kg CO₂","worksite_location":""})
        f2.update_traces(texttemplate="%{text} employees",textposition="outside",textfont_color=TEXT)
        f2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(T(f2,"Emissions by Worksite Location"),use_container_width=True)
    with col2:
        f2b=px.scatter(fdf,x="round_trip_distance_miles",y="co2_tonnes",color="commute_mode",
                       color_discrete_sequence=COLORS,opacity=0.5,
                       labels={"round_trip_distance_miles":"Round Trip Distance (miles)","co2_tonnes":"kg CO₂","commute_mode":"Mode"})
        st.plotly_chart(T(f2b,"Distance vs Emissions by Mode"),use_container_width=True)

# ══════════════════════════════════════════════
# DOWNSTREAM PAGE
# ══════════════════════════════════════════════
elif page == "Scope 3 — Cat 9: Downstream Transport":
    df,agg = get("downstream")
    st.markdown("# Scope 3 — Category 9: Downstream Transportation & Distribution")
    st.markdown("*Emissions = shipment weight (short tons) × distance × mode factor*")
    if df is None: st.error(errors.get("downstream","Unknown error")); st.stop()

    monthly_raw=agg["monthly"].copy()
    if "trip_id" in df.columns: id_col="trip_id"
    else: id_col="shipment_id"
    month_counts=df.groupby(["year","month"])[id_col].count().reset_index()
    month_counts.columns=["year","month","count"]
    avg_c=month_counts["count"].mean()
    monthly_clean=monthly_raw.merge(month_counts,on=["year","month"])
    monthly_clean=monthly_clean[monthly_clean["count"]>=avg_c*0.5]

    st.markdown("### Filters")
    fc1,fc2=st.columns(2)
    with fc1: sel_m=st.selectbox("Transport Mode",["All"]+sorted(df["mode_of_transport"].dropna().unique().tolist()))
    with fc2: sel_c=st.selectbox("Carrier",["All"]+sorted(df["carrier_name"].dropna().unique().tolist()))
    fdf=df.copy()
    if sel_m!="All": fdf=fdf[fdf["mode_of_transport"]==sel_m]
    if sel_c!="All": fdf=fdf[fdf["carrier_name"]==sel_c]
    fdf["route"]=fdf["origin"]+" → "+fdf["destination"]
    st.markdown("---")

    inv_col = "invoice_amount_usd" if "invoice_amount_usd" in fdf.columns else None
    k1,k2,k3,k4=st.columns(4)
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.0f} kg CO₂")
    with k2: st.metric("Shipments",f"{len(fdf):,}")
    with k3: st.metric("Avg Distance",f"{fdf['distance_traveled'].mean():,.0f} miles")
    with k4: st.metric("Total Invoice",f"${fdf[inv_col].sum():,.0f}" if inv_col else "N/A")
    st.markdown("---")

    # Monthly
    fig_t=px.line(monthly_clean,x="month_label",y="co2_tonnes",markers=True,color_discrete_sequence=["#ef4444"],labels={"month_label":"","co2_tonnes":"kg CO₂"})
    fig_t.update_traces(line_width=2.5,marker_size=7,marker_color="#ef4444",marker_line_color=BG)
    st.plotly_chart(T(fig_t,"Monthly Downstream Emissions (kg CO₂)"),use_container_width=True)
    st.markdown("---")

    # 1. Mode
    st.markdown('<div class="section-title">1. Emissions by Mode of Transport</div>',unsafe_allow_html=True)
    bm=fdf.groupby("mode_of_transport")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bm["mode_of_transport"]=bm["mode_of_transport"].str.capitalize()
    f1=px.bar(bm,x="mode_of_transport",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"mode_of_transport":"Mode","co2_tonnes":"kg CO₂"})
    f1.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
    st.plotly_chart(T(f1,"Emissions by Mode of Transport"),use_container_width=True)
    st.markdown("---")

    # 2. Routes + % emissions
    st.markdown('<div class="section-title">2. Emissions by Origin → Destination Pattern (% of emissions by route)</div>',unsafe_allow_html=True)
    br=fdf.groupby("route")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False).head(15)
    br["pct"]=(br["co2_tonnes"]/fdf["co2_tonnes"].sum()*100).round(1)
    col1,col2=st.columns([3,2])
    with col1:
        f2=px.bar(br,x="co2_tonnes",y="route",orientation="h",text="pct",color="co2_tonnes",
                  color_continuous_scale=[[0,"#4a1010"],[1,"#ef4444"]],labels={"co2_tonnes":"kg CO₂","route":""})
        f2.update_traces(texttemplate="%{text}%",textposition="outside",textfont_color=TEXT)
        f2.update_layout(coloraxis_showscale=False,height=500)
        st.plotly_chart(T(f2,"Top 15 Routes — % of Total Emissions"),use_container_width=True)
    with col2:
        rt=fdf.groupby("route").agg(shipments=(id_col,"count"),co2_tonnes=("co2_tonnes","sum")).reset_index().sort_values("co2_tonnes",ascending=False).head(15)
        rt["co2_tonnes"]=rt["co2_tonnes"].round(2); rt.columns=["Route","Shipments","CO₂ (t)"]
        st.markdown('<div class="section-title" style="margin-top:.5rem">Route Summary</div>',unsafe_allow_html=True)
        st.dataframe(rt,use_container_width=True,hide_index=True,height=490)
    st.markdown("---")

    # 3. Volume + Weight
    st.markdown('<div class="section-title">3. Emissions by Shipment Volume & Weight</div>',unsafe_allow_html=True)
    col1,col2=st.columns(2)
    with col1:
        if "by_volume" in agg:
            fv=px.bar(agg["by_volume"],x="volume_bin",y="co2_tonnes",color="volume_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"volume_bin":"Volume Quartile","co2_tonnes":"kg CO₂"})
            fv.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
            st.plotly_chart(T(fv,"Emissions by Shipment Volume Quartile"),use_container_width=True)
    with col2:
        fw=px.bar(agg["by_weight"],x="weight_bin",y="co2_tonnes",color="weight_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"weight_bin":"Weight Quartile","co2_tonnes":"kg CO₂"})
        fw.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(fw,"Emissions by Shipment Weight Quartile"),use_container_width=True)
    st.markdown("---")

    # 4. Cost
    if inv_col and "cost_by_mode" in agg:
        st.markdown('<div class="section-title">4. Invoice by Mode of Transport & Emissions</div>',unsafe_allow_html=True)
        cm=agg["cost_by_mode"]
        col1,col2=st.columns(2)
        with col1:
            f4=px.bar(cm,x="mode_of_transport",y="invoice",color="mode_of_transport",color_discrete_sequence=COLORS,text="invoice",labels={"mode_of_transport":"Mode","invoice":"Invoice ($)"})
            f4.update_traces(texttemplate="$%{text:,.0f}",textposition="outside",showlegend=False,textfont_color=TEXT)
            st.plotly_chart(T(f4,"Invoice by Transport Mode"),use_container_width=True)
        with col2:
            f4b=px.scatter(fdf,x=inv_col,y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={inv_col:"Invoice ($)","co2_tonnes":"kg CO₂","mode_of_transport":"Mode"})
            st.plotly_chart(T(f4b,"Invoice vs Emissions"),use_container_width=True)
        cd=cm[["mode_of_transport","invoice","co2_tonnes","cost_per_tonne"]].copy()
        cd.columns=["Mode","Total Invoice ($)","CO₂ (t)","$/tonne CO₂e"]
        cd["Total Invoice ($)"]=cd["Total Invoice ($)"].round(0); cd["CO₂ (t)"]=cd["CO₂ (t)"].round(2)
        st.dataframe(cd,use_container_width=True,hide_index=True)

    st.markdown("""
    <div class="insight-box">
    <strong>Methodology:</strong> Downstream transport emissions calculated using distance-based method.
    Emission factors: Road 0.186, Rail 0.021, Water 0.077, Air 1.086 kg CO₂e per short ton-mile.
    Scope 3 Category 9 per GHG Protocol Corporate Standard (WRI/WBCSD).
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# SCOPE 1 EV TRANSPORT PAGE
# ══════════════════════════════════════════════
elif page == "Scope 1 — EV Transport":
    df,agg = get("ev")
    st.markdown("# Scope 1 — EV Transport Emissions")
    st.markdown("*Emissions sourced from pre-calculated dataset fields (gasoline, diesel, electric, hybrid)*")
    if df is None: st.error(errors.get("ev","Unknown error")); st.stop()

    st.markdown("### Filters")
    fc1,fc2 = st.columns(2)
    with fc1: sel_vt=st.selectbox("Vehicle Type",["All"]+sorted(df["vehicle_type_class_id"].dropna().unique().tolist()))
    with fc2: sel_pt=st.selectbox("Powertrain",["All"]+sorted(df["fuel_type_powertrain"].dropna().unique().tolist()))
    fdf=df.copy()
    if sel_vt!="All": fdf=fdf[fdf["vehicle_type_class_id"]==sel_vt]
    if sel_pt!="All": fdf=fdf[fdf["fuel_type_powertrain"]==sel_pt]
    st.markdown("---")

    k1,k2,k3,k4 = st.columns(4)
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.0f} kg CO₂")
    with k2: st.metric("Total Trips",f"{len(fdf):,}")
    with k3: st.metric("Total Miles",f"{fdf['distance_traveled'].sum():,.0f}")
    with k4: st.metric("Cost Analysis","N/A")
    st.markdown("---")

    # 1. Emissions by Vehicle Type
    st.markdown('<div class="section-title">1. Emissions by Vehicle Type</div>',unsafe_allow_html=True)
    bv = fdf.groupby("vehicle_type_class_id")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    col1,col2 = st.columns(2)
    with col1:
        f1=px.bar(bv,x="vehicle_type_class_id",y="co2_tonnes",color="vehicle_type_class_id",
                  color_discrete_sequence=COLORS,text="co2_tonnes",
                  labels={"vehicle_type_class_id":"Vehicle Type","co2_tonnes":"kg CO₂"})
        f1.update_traces(texttemplate="%{text:,.2f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f1,"Emissions by Vehicle Type"),use_container_width=True)
    with col2:
        f1b=px.pie(bv,values="co2_tonnes",names="vehicle_type_class_id",
                   color_discrete_sequence=COLORS,hole=0.4)
        f1b.update_traces(textfont_color="#f9fafb",textfont_size=12,marker_line_color=BG,marker_line_width=2)
        f1b=pie(f1b); f1b.update_layout(title_text="% Share by Vehicle Type")
        st.plotly_chart(f1b,use_container_width=True)
    st.markdown("---")

    # 2. Miles Traveled by Vehicle Type
    st.markdown('<div class="section-title">2. Miles Traveled by Vehicle Type</div>',unsafe_allow_html=True)
    mv = fdf.groupby("vehicle_type_class_id")["distance_traveled"].sum().reset_index().sort_values("distance_traveled",ascending=False)
    f2=px.bar(mv,x="vehicle_type_class_id",y="distance_traveled",color="vehicle_type_class_id",
              color_discrete_sequence=COLORS,text="distance_traveled",
              labels={"vehicle_type_class_id":"Vehicle Type","distance_traveled":"Miles Traveled"})
    f2.update_traces(texttemplate="%{text:,.0f}",textposition="outside",showlegend=False,textfont_color=TEXT)
    st.plotly_chart(T(f2,"Miles Traveled by Vehicle Type"),use_container_width=True)
    st.markdown("---")

    # 3. Emissions Per Mile by Vehicle Type
    st.markdown('<div class="section-title">3. Emissions Per Mile by Vehicle Type</div>',unsafe_allow_html=True)
    epm = fdf.groupby("vehicle_type_class_id").agg(
        co2_kg=("co2_kg","sum"),
        miles=("distance_traveled","sum")
    ).reset_index()
    epm["kg_per_mile"] = (epm["co2_kg"] / epm["miles"].replace(0,np.nan)).round(4)
    epm = epm.sort_values("kg_per_mile",ascending=False)
    col1,col2 = st.columns(2)
    with col1:
        f3=px.bar(epm,x="vehicle_type_class_id",y="kg_per_mile",color="vehicle_type_class_id",
                  color_discrete_sequence=COLORS,text="kg_per_mile",
                  labels={"vehicle_type_class_id":"Vehicle Type","kg_per_mile":"kg CO₂e per Mile"})
        f3.update_traces(texttemplate="%{text:.4f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f3,"Emissions Intensity (kg CO₂e per Mile)"),use_container_width=True)
    with col2:
        # Also by powertrain
        pt_epm = fdf.groupby("fuel_type_powertrain").agg(co2_kg=("co2_kg","sum"),miles=("distance_traveled","sum")).reset_index()
        pt_epm["kg_per_mile"] = (pt_epm["co2_kg"] / pt_epm["miles"].replace(0,np.nan)).round(4)
        pt_epm = pt_epm.sort_values("kg_per_mile",ascending=False)
        f3b=px.bar(pt_epm,x="fuel_type_powertrain",y="kg_per_mile",color="fuel_type_powertrain",
                   color_discrete_sequence=COLORS,text="kg_per_mile",
                   labels={"fuel_type_powertrain":"Powertrain","kg_per_mile":"kg CO₂e per Mile"})
        f3b.update_traces(texttemplate="%{text:.4f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f3b,"Emissions Intensity by Powertrain"),use_container_width=True)
    st.markdown("---")

    # 4. Emissions by Origin → Destination Pattern (frequency)
    st.markdown('<div class="section-title">4. Emissions by Origin → Destination Pattern (frequency)</div>',unsafe_allow_html=True)
    br = fdf.groupby("route").agg(
        trips=("vehicle_id","count"),
        co2_tonnes=("co2_tonnes","sum"),
        miles=("distance_traveled","sum")
    ).reset_index().sort_values("co2_tonnes",ascending=False).head(15)
    br["pct"]=(br["co2_tonnes"]/br["co2_tonnes"].sum()*100).round(1)
    col1,col2 = st.columns([3,2])
    with col1:
        f4=px.bar(br,x="co2_tonnes",y="route",orientation="h",text="trips",
                  color="co2_tonnes",color_continuous_scale=[[0,"#064e4e"],[1,"#06b6d4"]],
                  labels={"co2_tonnes":"kg CO₂","route":""})
        f4.update_traces(texttemplate="%{text} trips",textposition="outside",textfont_color=TEXT)
        f4.update_layout(coloraxis_showscale=False,height=500)
        st.plotly_chart(T(f4,"Top 15 Routes by Emissions (with trip frequency)"),use_container_width=True)
    with col2:
        rt=br[["route","trips","co2_tonnes","pct"]].copy()
        rt["co2_tonnes"]=rt["co2_tonnes"].round(3)
        rt.columns=["Route","Trips","CO₂ (t)","% Share"]
        st.markdown('<div class="section-title" style="margin-top:.5rem">Route Summary</div>',unsafe_allow_html=True)
        st.dataframe(rt,use_container_width=True,hide_index=True,height=490)
    st.markdown("---")

    # 5. Cost Analysis — N/A
    st.markdown('<div class="section-title">5. Cost Analysis (Invoice)</div>',unsafe_allow_html=True)
    st.info("Cost analysis pending — invoice/cost data not available in current dataset.")

    st.markdown("""
    <div class="insight-box">
    <strong>Methodology:</strong> Emissions sourced from pre-calculated dataset columns
    (gasoline_emissions_kgco2, diesel_emissions_kgco2, electric_emissions_kgco2, hybrid1_emissions_kgco2).
    Total emissions = sum of all fuel-type emission components per trip.
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# ML — ANOMALY DETECTION PAGE
# ══════════════════════════════════════════════
elif page == "🤖 ML — Anomaly Detection":
    import io
    st.markdown("# 🤖 ML — Anomaly Detection")
    st.markdown("*IsolationForest model detecting statistically abnormal shipments across emission, cost, and distance features*")
    st.markdown("---")

    # ── CROSS-DATASET SUMMARY TABLE ─────────────
    st.markdown('<div class="section-title">📊 Anomaly Summary — All Datasets</div>', unsafe_allow_html=True)
    st.markdown("<small style='color:#9ca3af'>Overview of anomalies detected across all datasets at 5% contamination rate.</small>", unsafe_allow_html=True)

    summary_rows = []
    all_keys = {"Logistics (Cat 4)":"logistics","Downstream (Cat 9)":"downstream","Business Travel (Cat 6)":"business","EV Transport (Scope 1)":"ev"}
    for label, k in all_keys.items():
        df_s, _ = get(k)
        if df_s is None: continue
        cands = ['co2_kg','co2_tonnes','total_emissions_kgco2','distance_traveled','distance_miles',
                 'shipment_weight_lb','invoice_amount_usd','fuel_consumed_gallons','idle_time_minutes',
                 'round_trip_distance_miles','days_onsite_per_week','miles','passenger_count']
        avail_s = [c for c in cands if c in df_s.columns]
        if 'co2_kg' not in avail_s and 'co2_tonnes' in avail_s:
            df_s = df_s.copy(); df_s['co2_kg'] = df_s['co2_tonnes']; avail_s = ['co2_kg'] + avail_s
        feats_s = avail_s[:min(4, len(avail_s))]
        if len(feats_s) < 2: continue
        dm = df_s[feats_s].dropna()
        xs = StandardScaler().fit_transform(dm)
        ps = IsolationForest(n_estimators=100, contamination=0.05, random_state=42).fit_predict(xs)
        n_a = int((ps == -1).sum())
        co2_col_s = 'co2_kg' if 'co2_kg' in df_s.columns else 'co2_tonnes'
        anom_co2 = df_s.loc[dm.index[ps==-1], co2_col_s].sum() if co2_col_s in df_s.columns else 0
        summary_rows.append({"Dataset": label, "Records": len(dm), "Anomalies": n_a,
                              "Rate (%)": round(100*n_a/len(dm),1), "Anomalous CO₂ (kg)": round(anom_co2,1)})
    if summary_rows:
        sum_df = pd.DataFrame(summary_rows)
        col1, col2 = st.columns([2,1])
        with col1:
            fs = px.bar(sum_df, x="Dataset", y="Anomalies", color="Dataset",
                        color_discrete_sequence=COLORS, text="Anomalies")
            fs.update_traces(texttemplate="%{text}", textposition="outside", showlegend=False, textfont_color=TEXT)
            st.plotly_chart(T(fs, "Anomaly Count by Dataset"), use_container_width=True)
        with col2:
            st.markdown('<div class="section-title" style="margin-top:.5rem">Summary Table</div>', unsafe_allow_html=True)
            st.dataframe(sum_df, use_container_width=True, hide_index=True)
    st.markdown("---")

    # Dataset selector
    dataset_choice = st.selectbox("Select Dataset", [
        "Logistics (Cat 4)",
        "Downstream Transport (Cat 9)",
        "Business Travel (Cat 6)",
        "EV Transport (Scope 1)",
    ])

    contamination = st.slider(
        "Expected anomaly rate (%)",
        min_value=1, max_value=15, value=5, step=1,
        help="What % of records you expect to be anomalous. Default 5% is standard."
    ) / 100

    st.markdown("---")

    # Load correct dataset
    key_map = {
        "Logistics (Cat 4)": "logistics",
        "Downstream Transport (Cat 9)": "downstream",
        "Business Travel (Cat 6)": "business",
        "EV Transport (Scope 1)": "ev",
    }
    key = key_map[dataset_choice]
    df_raw, agg = get(key)

    if df_raw is None:
        st.error(f"Could not load {dataset_choice} data.")
        st.stop()

    # Select numeric features available in this dataset
    candidate_features = [
        'co2_kg', 'co2_tonnes', 'total_emissions_kgco2',
        'distance_traveled', 'distance_miles', 'actual_distance_miles',
        'shipment_weight_lb', 'shipment_weight_lbs', 'shipment_weight',
        'invoice_amount_usd', 'freight_invoice_usd',
        'fuel_consumed_gallons', 'fuel_gallons', 'fuel_quantity_gallons',
        'idle_time_min', 'idle_time_minutes', 'idle_time',
        'distance', 'miles', 'passenger_count',
        'round_trip_distance_miles', 'days_onsite_per_week',
    ]

    available = [c for c in candidate_features if c in df_raw.columns]

    # Always use co2_kg or co2_tonnes as primary
    if 'co2_kg' not in available and 'co2_tonnes' in available:
        df_raw = df_raw.copy()
        df_raw['co2_kg'] = df_raw['co2_tonnes']
        available = ['co2_kg'] + available

    if len(available) < 2:
        st.error("Not enough numeric features in this dataset for anomaly detection.")
        st.stop()

    # Let user pick features
    default_features = available[:min(4, len(available))]
    selected_features = st.multiselect(
        "Features used by the model",
        options=available,
        default=default_features,
        help="IsolationForest will use these columns to detect anomalies."
    )

    if len(selected_features) < 2:
        st.warning("Select at least 2 features.")
        st.stop()

    # Run model
    with st.spinner("Running IsolationForest..."):
        df_model = df_raw[selected_features].dropna()
        idx = df_model.index

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df_model)

        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=42
        )
        preds = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        df_result = df_raw.loc[idx].copy()
        df_result['anomaly_label'] = preds
        df_result['anomaly_score'] = scores
        df_result['is_anomaly'] = preds == -1

    n_anomalies = int(df_result['is_anomaly'].sum())
    n_total = len(df_result)
    pct = round(100 * n_anomalies / n_total, 1)

    # Emission savings potential
    co2_col = 'co2_kg' if 'co2_kg' in df_result.columns else ('co2_tonnes' if 'co2_tonnes' in df_result.columns else None)
    savings_kg = 0
    if co2_col:
        normal_mean = df_result[df_result['is_anomaly']==False][co2_col].mean()
        anom_mean   = df_result[df_result['is_anomaly']==True][co2_col].mean()
        savings_kg  = max(0, (anom_mean - normal_mean) * n_anomalies)

    # KPI row — now with meaningful dataset-specific values
    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(kpi("Total Records", f"{n_total:,}", "records analyzed", "#10b981"), unsafe_allow_html=True)
    with k2: st.markdown(kpi("Anomalies Detected", f"{n_anomalies:,}", f"{pct}% of total", "#ef4444"), unsafe_allow_html=True)
    with k3: st.markdown(kpi("Avg Anomaly CO₂", f"{df_result[df_result['is_anomaly']==True][co2_col].mean():,.0f}" if co2_col else "N/A", "kg CO₂ per record", "#f59e0b"), unsafe_allow_html=True)
    with k4: st.markdown(kpi("Emission Savings Potential", f"{savings_kg:,.0f}", "kg CO₂ if anomalies fixed", "#8b5cf6"), unsafe_allow_html=True)
    st.markdown("---")

    # ── 1. ANOMALY SCORE DISTRIBUTION ────────────
    st.markdown('<div class="section-title">1. Anomaly Score Distribution</div>', unsafe_allow_html=True)
    st.markdown("<small style='color:#9ca3af'>Lower scores = more anomalous. Red bars are flagged anomalies.</small>", unsafe_allow_html=True)
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Histogram(x=df_result[~df_result['is_anomaly']]['anomaly_score'], name='Normal', marker_color='#3b82f6', opacity=0.7, nbinsx=50))
    fig_dist.add_trace(go.Histogram(x=df_result[df_result['is_anomaly']]['anomaly_score'],  name='Anomaly', marker_color='#ef4444', opacity=0.9, nbinsx=50))
    fig_dist.update_layout(barmode='overlay')
    st.plotly_chart(T(fig_dist, "Anomaly Score Distribution — Normal vs Anomalous"), use_container_width=True)
    st.markdown("---")

    # ── 2. EMISSIONS VS DISTANCE SCATTER ─────────
    dist_col = next((c for c in ['distance_traveled','distance_miles','actual_distance_miles','miles','round_trip_distance_miles'] if c in df_result.columns), None)
    if co2_col and dist_col:
        st.markdown('<div class="section-title">2. Emissions vs Distance — Anomalies Highlighted</div>', unsafe_allow_html=True)
        plot_df = df_result[[co2_col, dist_col, 'is_anomaly', 'anomaly_score']].copy()
        plot_df['Status'] = plot_df['is_anomaly'].map({True: '🔴 Anomaly', False: '🔵 Normal'})
        fig_scatter = px.scatter(plot_df, x=dist_col, y=co2_col, color='Status',
            color_discrete_map={'🔴 Anomaly': '#ef4444', '🔵 Normal': '#3b82f6'},
            opacity=0.6, hover_data=['anomaly_score'],
            labels={dist_col: 'Distance (miles)', co2_col: 'Emissions (kg CO₂)'})
        fig_scatter.update_traces(marker=dict(size=5))
        st.plotly_chart(T(fig_scatter, "Emissions vs Distance — Red = flagged anomalies"), use_container_width=True)
        st.markdown("---")

    # ── 3. ANOMALIES BY MODE ──────────────────────
    mode_col = next((c for c in ['mode_of_transport','transport_mode','travel_mode','commute_mode','fuel_type_powertrain'] if c in df_result.columns), None)
    if mode_col:
        st.markdown('<div class="section-title">3. Anomaly Count by Transport Mode</div>', unsafe_allow_html=True)
        mode_anom = df_result.groupby(mode_col)['is_anomaly'].agg(['sum','count']).reset_index()
        mode_anom.columns = [mode_col, 'anomalies', 'total']
        mode_anom['anomaly_rate'] = (mode_anom['anomalies'] / mode_anom['total'] * 100).round(1)
        mode_anom = mode_anom.sort_values('anomalies', ascending=False)
        col1, col2 = st.columns(2)
        with col1:
            fb = px.bar(mode_anom, x=mode_col, y='anomalies', color=mode_col,
                        color_discrete_sequence=COLORS, text='anomalies',
                        labels={mode_col: 'Mode', 'anomalies': 'Anomaly Count'})
            fb.update_traces(texttemplate="%{text}", textposition="outside", showlegend=False, textfont_color=TEXT)
            st.plotly_chart(T(fb, "Anomaly Count by Mode"), use_container_width=True)
        with col2:
            fb2 = px.bar(mode_anom, x=mode_col, y='anomaly_rate', color=mode_col,
                         color_discrete_sequence=COLORS, text='anomaly_rate',
                         labels={mode_col: 'Mode', 'anomaly_rate': 'Anomaly Rate (%)'})
            fb2.update_traces(texttemplate="%{text:.1f}%", textposition="outside", showlegend=False, textfont_color=TEXT)
            st.plotly_chart(T(fb2, "Anomaly Rate (%) by Mode"), use_container_width=True)
        st.markdown("---")

    # ── 4. FEATURE IMPORTANCE ─────────────────────
    st.markdown('<div class="section-title">4. Feature Contribution to Anomaly Detection</div>', unsafe_allow_html=True)
    st.markdown("<small style='color:#9ca3af'>Shows how much each feature differs between anomalous and normal records. Higher = that feature is driving the anomaly flag.</small>", unsafe_allow_html=True)

    feat_importance = []
    for feat in selected_features:
        if feat not in df_result.columns: continue
        normal_mean_f = df_result[~df_result['is_anomaly']][feat].mean()
        anom_mean_f   = df_result[df_result['is_anomaly']][feat].mean()
        normal_std_f  = df_result[~df_result['is_anomaly']][feat].std()
        if normal_std_f > 0:
            z_diff = abs(anom_mean_f - normal_mean_f) / normal_std_f
        else:
            z_diff = 0
        pct_diff = ((anom_mean_f - normal_mean_f) / (abs(normal_mean_f) + 1e-9)) * 100
        feat_importance.append({"Feature": feat, "Z-Score Difference": round(z_diff, 3),
                                 "Anomaly Mean": round(anom_mean_f, 2), "Normal Mean": round(normal_mean_f, 2),
                                 "% Difference": round(pct_diff, 1)})

    if feat_importance:
        fi_df = pd.DataFrame(feat_importance).sort_values("Z-Score Difference", ascending=False)
        col1, col2 = st.columns([3, 2])
        with col1:
            ff = px.bar(fi_df, x="Z-Score Difference", y="Feature", orientation="h",
                        color="Z-Score Difference", color_continuous_scale=[[0,"#1e3a5f"],[1,"#ef4444"]],
                        text="Z-Score Difference",
                        labels={"Z-Score Difference": "Z-Score Δ (higher = stronger driver)"})
            ff.update_traces(texttemplate="%{text:.2f}", textposition="outside", textfont_color=TEXT)
            ff.update_layout(coloraxis_showscale=False, height=300)
            st.plotly_chart(T(ff, "Feature Importance — Which features drive anomaly flags"), use_container_width=True)
        with col2:
            st.markdown('<div class="section-title" style="margin-top:.5rem">Feature Comparison</div>', unsafe_allow_html=True)
            fi_display = fi_df[["Feature","Normal Mean","Anomaly Mean","% Difference"]].copy()
            fi_display["% Difference"] = fi_display["% Difference"].apply(lambda x: f"+{x:.1f}%" if x > 0 else f"{x:.1f}%")
            st.dataframe(fi_display, use_container_width=True, hide_index=True)
    st.markdown("---")

    # ── 5. CARRIER/SUPPLIER BREAKDOWN ────────────
    carrier_col = next((c for c in ['carrier_name','supplier_id','supplier_location','carrier_type','department'] if c in df_result.columns), None)
    if carrier_col:
        st.markdown(f'<div class="section-title">5. Anomaly Breakdown by {carrier_col.replace("_"," ").title()}</div>', unsafe_allow_html=True)
        carr_anom = df_result.groupby(carrier_col)['is_anomaly'].agg(['sum','count']).reset_index()
        carr_anom.columns = [carrier_col, 'anomalies', 'total']
        carr_anom['rate'] = (carr_anom['anomalies'] / carr_anom['total'] * 100).round(1)
        carr_anom = carr_anom[carr_anom['anomalies'] > 0].sort_values('anomalies', ascending=False).head(15)
        fc = px.bar(carr_anom, x=carrier_col, y='anomalies', color='rate',
                    color_continuous_scale=[[0,"#1e3a5f"],[1,"#ef4444"]],
                    text='anomalies', labels={carrier_col: carrier_col.replace("_"," ").title(), 'anomalies': 'Anomaly Count', 'rate': 'Rate (%)'})
        fc.update_traces(texttemplate="%{text}", textposition="outside", textfont_color=TEXT)
        fc.update_layout(coloraxis_colorbar=dict(title="Rate %"))
        st.plotly_chart(T(fc, f"Top 15 {carrier_col.replace('_',' ').title()}s by Anomaly Count"), use_container_width=True)
        st.markdown("---")

    # ── 6. EMISSION SAVINGS POTENTIAL ────────────
    if co2_col and savings_kg > 0:
        st.markdown('<div class="section-title">6. Emission Savings Potential</div>', unsafe_allow_html=True)
        st.markdown("<small style='color:#9ca3af'>If anomalous records were brought in line with normal averages, this is the estimated CO₂ reduction.</small>", unsafe_allow_html=True)

        normal_mean_co2 = df_result[~df_result['is_anomaly']][co2_col].mean()
        anom_mean_co2   = df_result[df_result['is_anomaly']][co2_col].mean()

        sav_col1, sav_col2, sav_col3 = st.columns(3)
        with sav_col1: st.markdown(kpi("Normal Avg Emissions", f"{normal_mean_co2:,.0f}", "kg CO₂ per record", "#10b981"), unsafe_allow_html=True)
        with sav_col2: st.markdown(kpi("Anomaly Avg Emissions", f"{anom_mean_co2:,.0f}", "kg CO₂ per record", "#ef4444"), unsafe_allow_html=True)
        with sav_col3: st.markdown(kpi("Total Savings Potential", f"{savings_kg:,.0f}", "kg CO₂ if anomalies fixed", "#8b5cf6"), unsafe_allow_html=True)

        # Savings bar
        sav_df = pd.DataFrame({"Category": ["Normal Average", "Anomaly Average"], "kg CO₂": [normal_mean_co2, anom_mean_co2]})
        fsav = px.bar(sav_df, x="Category", y="kg CO₂", color="Category",
                      color_discrete_map={"Normal Average":"#10b981","Anomaly Average":"#ef4444"},
                      text="kg CO₂")
        fsav.update_traces(texttemplate="%{text:,.0f}", textposition="outside", showlegend=False, textfont_color=TEXT)
        st.plotly_chart(T(fsav, "Normal vs Anomaly Average Emissions per Record"), use_container_width=True)
        st.markdown("---")

    # ── 7. TOP ANOMALOUS RECORDS + DOWNLOAD ──────
    st.markdown('<div class="section-title">7. Top Anomalous Records (Most Extreme First)</div>', unsafe_allow_html=True)
    top_anom = df_result[df_result['is_anomaly']].sort_values('anomaly_score').head(20)
    display_cols = [c for c in selected_features + ['anomaly_score'] if c in top_anom.columns]
    if mode_col and mode_col not in display_cols: display_cols = [mode_col] + display_cols
    if carrier_col and carrier_col not in display_cols: display_cols = [carrier_col] + display_cols
    top_display = top_anom[display_cols].copy()
    top_display['anomaly_score'] = top_display['anomaly_score'].round(4)
    st.dataframe(top_display.reset_index(drop=True), use_container_width=True, hide_index=True)

    # Download button — all anomalies as CSV
    all_anom = df_result[df_result['is_anomaly']].sort_values('anomaly_score')
    csv_buffer = io.StringIO()
    all_anom.to_csv(csv_buffer, index=False)
    st.download_button(
        label=f"⬇️ Download All {n_anomalies} Anomalies as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"anomalies_{key}_{n_anomalies}.csv",
        mime="text/csv"
    )

    st.markdown(f"""
    <div class="insight-box">
    <strong>Model:</strong> IsolationForest (sklearn) — 200 estimators, contamination={contamination:.0%}, random_state=42.<br>
    <strong>How it works:</strong> The model randomly partitions the feature space. Records isolated quickly (few splits) are anomalies — statistically different from the majority.<br>
    <strong>Features used:</strong> {', '.join(selected_features)}<br>
    <strong>Result:</strong> {n_anomalies:,} anomalies detected ({pct}%). Estimated savings if corrected: {savings_kg:,.0f} kg CO₂.
    </div>""", unsafe_allow_html=True)

