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
    with c1: st.markdown(kpi("Grand Total",f"{grand_total:,.1f}","tonnes CO₂e","#10b981"),unsafe_allow_html=True)
    with c2: st.markdown(kpi("Cat 4 Logistics",f"{totals['logistics']:,.1f}","tonnes CO₂e","#3b82f6"),unsafe_allow_html=True)
    with c3: st.markdown(kpi("Cat 6 Business Travel",f"{totals['business']:,.1f}","tonnes CO₂e","#f59e0b"),unsafe_allow_html=True)
    c4,c5,c6 = st.columns(3)
    with c4: st.markdown(kpi("Cat 7 Commute",f"{totals['commute']:,.1f}","tonnes CO₂e","#8b5cf6"),unsafe_allow_html=True)
    with c5: st.markdown(kpi("Cat 9 Downstream",f"{totals['downstream']:,.1f}","tonnes CO₂e","#ef4444"),unsafe_allow_html=True)
    with c6: st.markdown(kpi("Scope 1 — EV Transport",f"{totals['ev']:,.1f}","tonnes CO₂e","#06b6d4"),unsafe_allow_html=True)

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
                      labels={"CO2_tonnes":"Tonnes CO₂e","Category":""})
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
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.2f} t CO₂e")
    with k2: st.metric("Shipments",f"{len(fdf):,}")
    with k3: st.metric("Avg Distance",f"{fdf['distance_traveled'].mean():,.0f} miles")
    with k4: st.metric("Total Invoice",f"${fdf['invoice_amount_usd'].sum():,.0f}")
    st.markdown("---")

    # 1. Mode
    st.markdown('<div class="section-title">1. Emissions by Mode of Transport</div>',unsafe_allow_html=True)
    bm=fdf.groupby("mode_of_transport")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bm["mode_of_transport"]=bm["mode_of_transport"].str.capitalize()
    f1=px.bar(bm,x="mode_of_transport",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,
              text="co2_tonnes",labels={"mode_of_transport":"Mode","co2_tonnes":"Tonnes CO₂e"})
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
        f2=px.bar(vagg,x="volume_bin",y="co2_tonnes",color="volume_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"volume_bin":"Volume Quartile","co2_tonnes":"Tonnes CO₂e"})
        f2.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
        st.plotly_chart(T(f2,"Emissions by Volume Quartile"),use_container_width=True)
    with col2:
        f2b=px.scatter(fdf,x="shipment_volume_ctf",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,labels={"shipment_volume_ctf":"Volume (cu ft)","co2_tonnes":"Tonnes CO₂e","mode_of_transport":"Mode"})
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
                   color="co2_tonnes",color_continuous_scale=[[0,"#1e3a5f"],[1,"#3b82f6"]],labels={"co2_tonnes":"Tonnes CO₂e","carrier_name":""})
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
                  color_continuous_scale=[[0,"#064e3b"],[1,"#10b981"]],labels={"co2_tonnes":"Tonnes CO₂e","route":""})
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
        f5b=px.scatter(fdf,x="invoice_amount_usd",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={"invoice_amount_usd":"Invoice ($)","co2_tonnes":"Tonnes CO₂e","mode_of_transport":"Mode"})
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
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.2f} t CO₂e")
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
        f1=px.bar(bm,x="travel_mode",y="co2_tonnes",color="travel_mode",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"travel_mode":"Mode","co2_tonnes":"Tonnes CO₂e"})
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
        f2=px.bar(bp,x="trip_purpose",y="co2_tonnes",color="trip_purpose",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"trip_purpose":"Purpose","co2_tonnes":"Tonnes CO₂e"})
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
                  color_continuous_scale=[[0,"#1e3a5f"],[1,"#f59e0b"]],labels={"co2_tonnes":"Tonnes CO₂e","route":""})
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
        f4b=px.scatter(fdf,x="invoice_amount_usd",y="co2_tonnes",color="travel_mode",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={"invoice_amount_usd":"Invoice ($)","co2_tonnes":"Tonnes CO₂e","travel_mode":"Mode"})
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
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.2f} t CO₂e")
    with k2: st.metric("Employees",f"{len(fdf):,}")
    with k3: st.metric("Avg per Employee",f"{fdf['co2_tonnes'].mean()*1000:,.0f} kg CO₂e")
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
                   labels={"commute_mode":"Mode","co2_tonnes":"Tonnes CO₂e"})
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
                  text="employees",labels={"co2_tonnes":"Tonnes CO₂e","worksite_location":""})
        f2.update_traces(texttemplate="%{text} employees",textposition="outside",textfont_color=TEXT)
        f2.update_layout(coloraxis_showscale=False)
        st.plotly_chart(T(f2,"Emissions by Worksite Location"),use_container_width=True)
    with col2:
        f2b=px.scatter(fdf,x="round_trip_distance_miles",y="co2_tonnes",color="commute_mode",
                       color_discrete_sequence=COLORS,opacity=0.5,
                       labels={"round_trip_distance_miles":"Round Trip Distance (miles)","co2_tonnes":"Tonnes CO₂e","commute_mode":"Mode"})
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
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.2f} t CO₂e")
    with k2: st.metric("Shipments",f"{len(fdf):,}")
    with k3: st.metric("Avg Distance",f"{fdf['distance_traveled'].mean():,.0f} miles")
    with k4: st.metric("Total Invoice",f"${fdf[inv_col].sum():,.0f}" if inv_col else "N/A")
    st.markdown("---")

    # Monthly
    fig_t=px.line(monthly_clean,x="month_label",y="co2_tonnes",markers=True,color_discrete_sequence=["#ef4444"],labels={"month_label":"","co2_tonnes":"Tonnes CO₂e"})
    fig_t.update_traces(line_width=2.5,marker_size=7,marker_color="#ef4444",marker_line_color=BG)
    st.plotly_chart(T(fig_t,"Monthly Downstream Emissions (tonnes CO₂e)"),use_container_width=True)
    st.markdown("---")

    # 1. Mode
    st.markdown('<div class="section-title">1. Emissions by Mode of Transport</div>',unsafe_allow_html=True)
    bm=fdf.groupby("mode_of_transport")["co2_tonnes"].sum().reset_index().sort_values("co2_tonnes",ascending=False)
    bm["mode_of_transport"]=bm["mode_of_transport"].str.capitalize()
    f1=px.bar(bm,x="mode_of_transport",y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"mode_of_transport":"Mode","co2_tonnes":"Tonnes CO₂e"})
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
                  color_continuous_scale=[[0,"#4a1010"],[1,"#ef4444"]],labels={"co2_tonnes":"Tonnes CO₂e","route":""})
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
            fv=px.bar(agg["by_volume"],x="volume_bin",y="co2_tonnes",color="volume_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"volume_bin":"Volume Quartile","co2_tonnes":"Tonnes CO₂e"})
            fv.update_traces(texttemplate="%{text:,.1f}",textposition="outside",showlegend=False,textfont_color=TEXT)
            st.plotly_chart(T(fv,"Emissions by Shipment Volume Quartile"),use_container_width=True)
    with col2:
        fw=px.bar(agg["by_weight"],x="weight_bin",y="co2_tonnes",color="weight_bin",color_discrete_sequence=COLORS,text="co2_tonnes",labels={"weight_bin":"Weight Quartile","co2_tonnes":"Tonnes CO₂e"})
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
            f4b=px.scatter(fdf,x=inv_col,y="co2_tonnes",color="mode_of_transport",color_discrete_sequence=COLORS,opacity=0.5,trendline="ols",trendline_scope="overall",trendline_color_override="#f9fafb",labels={inv_col:"Invoice ($)","co2_tonnes":"Tonnes CO₂e","mode_of_transport":"Mode"})
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
    with k1: st.metric("Total Emissions",f"{fdf['co2_tonnes'].sum():,.2f} t CO₂e")
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
                  labels={"vehicle_type_class_id":"Vehicle Type","co2_tonnes":"Tonnes CO₂e"})
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
                  labels={"co2_tonnes":"Tonnes CO₂e","route":""})
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
