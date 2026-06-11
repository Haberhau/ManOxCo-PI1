"""
ManOxCo LCS — Momentum Data Intelligence Platform
Run: streamlit run app/main.py
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import timedelta
import sys, json, os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[1] / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from components.data import (
    load_risk, load_production, load_financial,
    load_consumption, load_delivery, latest_risk_snapshot,
)
from components.style import inject_css, page_header, section_heading, stat_block

# ── Constants ─────────────────────────────────────────────────────────────────
DARK = dict(
    plot_bgcolor="10131C", paper_bgcolor="10131C",
    font=dict(family="IBM Plex Mono, monospace", color="#8A94A8", size=11),
    xaxis=dict(gridcolor="#1D2235", linecolor="#1D2235", tickfont=dict(size=10, color="#50586A")),
    yaxis=dict(gridcolor="#1D2235", linecolor="#1D2235", tickfont=dict(size=10, color="#50586A")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#8A94A8")),
    margin=dict(l=10, r=20, t=30, b=10),
)
def dark(**kw):
    d = dict(
        plot_bgcolor="#10131C", paper_bgcolor="#10131C",
        font=dict(family="IBM Plex Mono, monospace", color="#8A94A8", size=11),
        xaxis=dict(gridcolor="#1D2235", linecolor="#1D2235", tickfont=dict(size=10, color="#50586A")),
        yaxis=dict(gridcolor="#1D2235", linecolor="#1D2235", tickfont=dict(size=10, color="#50586A")),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#8A94A8")),
        margin=dict(l=10, r=20, t=30, b=10),
    )
    d.update(kw)
    return d

RISK_COLOR = {"CRITICAL":"#E53E4D","HIGH":"#F07030","MEDIUM":"#E5B830","LOW":"#10C87A"}
PLANT_COLOR = {"Madrid":"#F0A500","Barcelona":"#18A8C8","Zaragoza":"#10C87A",
               "Alicante":"#8B5CF6","Gijon":"#F07030"}
PAGES = ["Command Centre","Hospital Risk","Plant Operations",
         "Financial","Maintenance","Demand Forecast","AI Copilot"]

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Momentum · ManOxCo", page_icon="⬡",
                   layout="wide", menu_items={})
inject_css()

# ── Page routing ──────────────────────────────────────────────────────────────
if "page" not in st.query_params or st.query_params["page"] not in PAGES:
    st.query_params["page"] = "Command Centre"
page = st.query_params["page"]

# ── Two-column layout: nav | content ──────────────────────────────────────────
nav, content = st.columns([1, 4])

# ════════════════════════════════════════════════════════════════════════════
# NAV COLUMN
# ════════════════════════════════════════════════════════════════════════════
with nav:
    st.markdown("""
    <div style='padding:1.4rem 0 1.2rem 0;border-bottom:1px solid #1D2235;margin-bottom:0.8rem'>
      <div style='font-family:Syne,sans-serif;font-size:1.2rem;font-weight:800;
                  color:#F0A500;letter-spacing:0.04em'>MOMENTUM</div>
      <div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;
                  color:#374151;margin-top:0.15rem;letter-spacing:0.08em'>
        Data Intelligence Platform</div>
    </div>""", unsafe_allow_html=True)

    for i, p in enumerate(PAGES):
        active = p == page
        st.markdown(
            f"<div style='padding:0.42rem 0.65rem;border-radius:4px;margin-bottom:2px;"
            f"font-family:DM Sans,sans-serif;font-size:0.83rem;"
            f"font-weight:{'600' if active else '400'};"
            f"color:{'#F0A500' if active else '#4B5563'};"
            f"background:{'rgba(240,165,0,0.09)' if active else 'transparent'};"
            f"border-left:{'2px solid #F0A500' if active else '2px solid transparent'}'>"
            f"<span style='font-family:IBM Plex Mono,monospace;font-size:0.62rem;"
            f"color:{'#F0A500' if active else '#374151'};margin-right:0.5rem'>{i+1:02d}</span>"
            f"{p}</div>",
            unsafe_allow_html=True,
        )
        if st.button(p, key=f"nav_{p}"):
            st.query_params["page"] = p
            st.rerun()

    st.markdown("<div style='border-top:1px solid #1D2235;margin:1rem 0'></div>",
                unsafe_allow_html=True)

    # Filters
    snap = latest_risk_snapshot()
    if page in ("Command Centre", "Hospital Risk"):
        cities = ["All cities"] + sorted(snap["hospital_city"].dropna().unique().tolist())
        sel_city = st.selectbox("City", cities, key="f_city")
        sel_risk = st.selectbox("Risk", ["All levels","CRITICAL","HIGH","MEDIUM","LOW"], key="f_risk")
    else:
        sel_city, sel_risk = "All cities", "All levels"

    if page == "Plant Operations":
        prod_ref = load_production()
        sel_plant = st.selectbox("Plant", sorted(prod_ref["plant"].dropna().unique()), key="f_plant")
    else:
        sel_plant = "Madrid"

    st.markdown("<div style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;"
                "color:#1F2937;margin-top:1.5rem;line-height:1.9'>ManOxCo × Momentum<br>"
                "PI-1 · 2024 Baseline</div>", unsafe_allow_html=True)


def filtered(df):
    if sel_city != "All cities":
        df = df[df["hospital_city"] == sel_city]
    if sel_risk != "All levels":
        df = df[df["risk_level"] == sel_risk]
    return df


# ════════════════════════════════════════════════════════════════════════════
# CONTENT COLUMN
# ════════════════════════════════════════════════════════════════════════════
with content:

    # ── 01 Command Centre ────────────────────────────────────────────────────
    if page == "Command Centre":
        page_header("Momentum · ManOxCo", "Oxygen Reliability Command Centre",
                    "LOX supply chain intelligence — live network status")

        view = filtered(snap)
        rc = view["risk_level"].value_counts()
        crit = view[view["risk_level"] == "CRITICAL"].sort_values("fill_pct")
        high = view[view["risk_level"] == "HIGH"].sort_values("fill_pct")

        # KPIs
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1: stat_block("Hospitals", str(len(view)))
        with k2:
            n = int(rc.get("CRITICAL", 0))
            stat_block("Critical", str(n), "dispatch now" if n else "clear",
                       "danger" if n else "")
        with k3:
            n = int(rc.get("HIGH", 0))
            stat_block("High", str(n), "urgent" if n else "clear",
                       "warning" if n else "")
        with k4: stat_block("Medium", str(int(rc.get("MEDIUM", 0))))
        with k5: stat_block("Safe", str(int(rc.get("LOW", 0))), variant="safe")

        st.markdown("---")
        section_heading("Active alerts")

        if crit.empty and high.empty:
            st.markdown("<div class='m-alert safe'><div class='m-alert-dot'></div>"
                        "<div class='m-alert-body'><div class='m-alert-name'>Network nominal</div>"
                        "<div class='m-alert-detail'>No hospitals below threshold</div>"
                        "</div></div>", unsafe_allow_html=True)
        for _, r in crit.iterrows():
            dtd = f"{r['days_to_dryout']:.0f}d" if r['days_to_dryout'] < 999 else "∞"
            st.markdown(
                f"<div class='m-alert crit'><div class='m-alert-dot'></div>"
                f"<div class='m-alert-body'>"
                f"<div class='m-alert-name'>{r['hospital_name']}</div>"
                f"<div class='m-alert-detail'>{r['hospital_city']} · "
                f"Fill <strong>{r['fill_pct']*100:.1f}%</strong> · "
                f"Dry-out <strong>{dtd}</strong></div></div></div>",
                unsafe_allow_html=True)
        for _, r in high.iterrows():
            dtd = f"{r['days_to_dryout']:.0f}d" if r['days_to_dryout'] < 999 else "∞"
            st.markdown(
                f"<div class='m-alert high'><div class='m-alert-dot'></div>"
                f"<div class='m-alert-body'>"
                f"<div class='m-alert-name'>{r['hospital_name']}</div>"
                f"<div class='m-alert-detail'>{r['hospital_city']} · "
                f"Fill <strong>{r['fill_pct']*100:.1f}%</strong> · "
                f"Dry-out <strong>{dtd}</strong></div></div></div>",
                unsafe_allow_html=True)

        st.markdown("---")
        section_heading("Network fill level — all hospitals")
        sv = view.sort_values("fill_pct").reset_index(drop=True)
        fig = go.Figure()
        for lvl, col in RISK_COLOR.items():
            sub = sv[sv["risk_level"] == lvl]
            if sub.empty: continue
            fig.add_trace(go.Bar(
                x=sub["fill_pct"]*100, y=sub["hospital_name"],
                orientation="h", name=lvl, marker_color=col, marker_line_width=0,
                text=sub["fill_pct"].apply(lambda v: f"{v*100:.0f}%"),
                textposition="outside", textfont=dict(size=10, color="#8A94A8"),
                hovertemplate="<b>%{y}</b><br>Fill: %{x:.1f}%<extra></extra>",
            ))
        fig.add_vline(x=12, line_dash="dash", line_color="#E53E4D", line_width=1,
                      annotation_text="Min 12%",
                      annotation_font=dict(size=9, color="#E53E4D"))
        fig.update_layout(**dark(height=550, barmode="stack",
            xaxis=dict(gridcolor="#1D2235", linecolor="#1D2235",
                       tickfont=dict(size=10, color="#50586A"),
                       range=[0,130], ticksuffix="%",
                       title=dict(text="fill level (%)", font=dict(size=10, color="#50586A"))),
            yaxis=dict(gridcolor="#1D2235", linecolor="#1D2235",
                       tickfont=dict(size=10, color="#8A94A8"), autorange="reversed"),
            legend=dict(orientation="h", y=1.03, x=0,
                        font=dict(size=10, color="#8A94A8"), bgcolor="rgba(0,0,0,0)"),
        ))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        section_heading("Plant status — last 30 days")
        prod = load_production()
        l30 = prod[prod["date"] >= prod["date"].max() - timedelta(30)]
        ps = l30.groupby("plant").agg(
            avg_prod=("production_tons","mean"),
            avg_util=("utilisation_pct","mean")
        ).reset_index().sort_values("plant")
        pcols = st.columns(len(ps))
        for col, (_, r) in zip(pcols, ps.iterrows()):
            c = PLANT_COLOR.get(r["plant"], "#F0A500")
            col.markdown(
                f"<div class='m-plant-card' style='border-top:2px solid {c}'>"
                f"<div class='m-plant-name'>{r['plant']}</div>"
                f"<div class='m-plant-value' style='color:{c}'>{r['avg_prod']:.2f}</div>"
                f"<div class='m-plant-unit'>tons / day avg</div>"
                f"<div class='m-plant-util'>util {r['avg_util']*100:.0f}%</div>"
                f"</div>", unsafe_allow_html=True)


    # ── 02 Hospital Risk ─────────────────────────────────────────────────────
    elif page == "Hospital Risk":
        page_header("Hospital Intelligence", "Risk Monitor",
                    "Rolling fill-level estimates · threshold alerts · delivery history")

        risk = load_risk()
        view = filtered(snap).sort_values("fill_pct")

        section_heading("Current snapshot")
        bmap = {"CRITICAL":"crit","HIGH":"high","MEDIUM":"medium","LOW":"low"}
        rows_html = ""
        for _, r in view.iterrows():
            b = bmap.get(r["risk_level"],"low")
            dtd = f"{r['days_to_dryout']:.0f}d" if r['days_to_dryout'] < 999 else "—"
            rows_html += (
                f"<tr>"
                f"<td style='padding:0.55rem 0.8rem;font-family:DM Sans,sans-serif;"
                f"font-size:0.88rem;color:#E8EDF8;border-bottom:1px solid #1D2235'>"
                f"{r['hospital_name']}</td>"
                f"<td style='padding:0.55rem 0.8rem;font-family:IBM Plex Mono,monospace;"
                f"font-size:0.78rem;color:#8A94A8;border-bottom:1px solid #1D2235'>"
                f"{r['hospital_city']}</td>"
                f"<td style='padding:0.55rem 0.8rem;font-family:IBM Plex Mono,monospace;"
                f"font-size:0.85rem;font-weight:600;color:#F0A500;border-bottom:1px solid #1D2235'>"
                f"{r['fill_pct']*100:.1f}%</td>"
                f"<td style='padding:0.55rem 0.8rem;border-bottom:1px solid #1D2235'>"
                f"<span class='m-badge {b}'>{r['risk_level']}</span></td>"
                f"<td style='padding:0.55rem 0.8rem;font-family:IBM Plex Mono,monospace;"
                f"font-size:0.78rem;color:#8A94A8;border-bottom:1px solid #1D2235'>{dtd}</td>"
                f"</tr>"
            )
        th = ("background:#161923;border-bottom:1px solid #1D2235;text-align:left;"
              "padding:0.55rem 0.8rem;font-family:IBM Plex Mono,monospace;"
              "font-size:0.65rem;letter-spacing:0.15em;text-transform:uppercase;color:#50586A")
        st.markdown(
            f"<div style='background:#10131C;border:1px solid #1D2235;border-radius:6px;"
            f"overflow:hidden;margin-bottom:1.5rem'><table style='width:100%;border-collapse:collapse'>"
            f"<thead><tr>"
            f"<th style='{th}'>Hospital</th><th style='{th}'>City</th>"
            f"<th style='{th}'>Fill</th><th style='{th}'>Risk</th>"
            f"<th style='{th}'>Days to dry-out</th>"
            f"</tr></thead><tbody>{rows_html}</tbody></table></div>",
            unsafe_allow_html=True)

        section_heading("Fill level over time")
        hospitals = sorted(view["hospital_name"].tolist())
        crit_names = view[view["risk_level"]=="CRITICAL"]["hospital_name"].tolist()
        def_idx = hospitals.index(crit_names[0]) if crit_names else 0
        sel_h = st.selectbox("Select hospital", hospitals, index=def_idx)

        h_risk = risk[risk["hospital_name"]==sel_h].sort_values("date")
        deliv = load_delivery()
        h_del = deliv[deliv["hospital_name"]==sel_h]

        fig = go.Figure()
        fig.add_hrect(y0=0, y1=12, fillcolor="rgba(229,62,77,0.05)", line_width=0)
        fig.add_trace(go.Scatter(
            x=h_risk["date"], y=h_risk["fill_pct"]*100,
            mode="lines", name="Fill %",
            line=dict(color="#F0A500", width=2),
            fill="tozeroy", fillcolor="rgba(240,165,0,0.06)"))
        fig.add_hline(y=12, line_dash="dash", line_color="#E53E4D", line_width=1,
                      annotation_text="critical (12%)",
                      annotation_font=dict(size=9, color="#E53E4D"))
        if not h_del.empty:
            dr = h_del.groupby("date")["refill_tons"].sum().reset_index()
            fig.add_trace(go.Scatter(
                x=dr["date"], y=[8]*len(dr), mode="markers",
                marker=dict(symbol="triangle-up", size=9, color="#10C87A"),
                name="Delivery"))
        fig.update_layout(**dark(height=360,
            yaxis=dict(gridcolor="#1D2235", linecolor="#1D2235",
                       tickfont=dict(size=10, color="#50586A"),
                       title=dict(text="fill (%)", font=dict(size=10, color="#50586A")),
                       range=[0,115]),
            legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10, color="#8A94A8"))))
        st.plotly_chart(fig, use_container_width=True)


    # ── 03 Plant Operations ──────────────────────────────────────────────────
    elif page == "Plant Operations":
        page_header("OT Data", "Plant Operations",
                    "Production volumes · storage levels · efficiency")

        prod = load_production()
        pdata = prod[prod["plant"]==sel_plant]
        l30 = pdata[pdata["date"] >= pdata["date"].max() - timedelta(30)]
        col_c = PLANT_COLOR.get(sel_plant, "#F0A500")

        k1, k2, k3 = st.columns(3)
        with k1: stat_block("Avg daily prod",  f"{l30['production_tons'].mean():.2f}t", "last 30 days")
        with k2: stat_block("Avg utilisation", f"{l30['utilisation_pct'].mean()*100:.0f}%")
        with k3: stat_block("Latest stored",   f"{pdata.sort_values('date').iloc[-1]['stored_tons']:.1f}t")

        st.markdown("---")
        section_heading(f"{sel_plant} — production & storage over time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pdata["date"], y=pdata["stored_tons"],
            mode="lines", name="Stored (t)",
            fill="tozeroy", fillcolor="rgba(240,165,0,0.07)",
            line=dict(color=col_c, width=2)))
        fig.add_trace(go.Scatter(
            x=pdata["date"], y=pdata["production_tons"],
            mode="lines", name="Daily prod (t)",
            line=dict(color="#18A8C8", width=1.5, dash="dot")))
        fig.update_layout(**dark(height=340,
            legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10))))
        st.plotly_chart(fig, use_container_width=True)

        section_heading("Monthly output — all plants")
        monthly = (
            prod.assign(month=lambda d: d["date"].dt.to_period("M").dt.to_timestamp())
            .groupby(["month","plant"])["production_tons"].sum().reset_index()
        )
        fig2 = go.Figure()
        for p in sorted(monthly["plant"].unique()):
            sub = monthly[monthly["plant"]==p]
            fig2.add_trace(go.Scatter(
                x=sub["month"], y=sub["production_tons"], mode="lines", name=p,
                line=dict(color=PLANT_COLOR.get(p,"#F0A500"), width=2)))
        fig2.update_layout(**dark(height=320,
            legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10))))
        st.plotly_chart(fig2, use_container_width=True)

        section_heading("Utilisation by plant")
        util = (prod.groupby("plant")["utilisation_pct"].mean()
                .reset_index().sort_values("utilisation_pct"))
        fig3 = go.Figure(go.Bar(
            x=util["utilisation_pct"]*100, y=util["plant"], orientation="h",
            marker_color=[PLANT_COLOR.get(p,"#F0A500") for p in util["plant"]],
            marker_line_width=0,
            text=util["utilisation_pct"].apply(lambda v: f"{v*100:.1f}%"),
            textposition="outside", textfont=dict(size=10, color="#8A94A8")))
        fig3.update_layout(**dark(height=280, showlegend=False,
            xaxis=dict(gridcolor="#1D2235", linecolor="#1D2235",
                       tickfont=dict(size=10, color="#50586A"),
                       range=[0,115], ticksuffix="%")))
        st.plotly_chart(fig3, use_container_width=True)


    # ── 04 Financial ─────────────────────────────────────────────────────────
    elif page == "Financial":
        page_header("Financial Intelligence", "Cost · Revenue · Margin",
                    "Monthly P&L across all ManOxCo plants")

        fin = load_financial()
        tot_rev  = fin["total_revenue"].sum()
        tot_cost = fin["total_cost"].sum()
        gross    = tot_rev - tot_cost
        margin   = gross/tot_rev*100 if tot_rev else 0

        k1, k2, k3, k4 = st.columns(4)
        with k1: stat_block("Total revenue", f"€{tot_rev/1e6:.2f}M")
        with k2: stat_block("Total cost",    f"€{tot_cost/1e6:.2f}M")
        with k3: stat_block("Gross margin",  f"€{gross/1e6:.2f}M")
        with k4: stat_block("Margin %",      f"{margin:.1f}%",
                             variant="safe" if margin > 0 else "danger")

        st.markdown("---")
        section_heading("Monthly revenue vs cost vs margin")
        m = fin.groupby("date")[["total_revenue","total_cost","gross_margin"]].sum().reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=m["date"], y=m["total_revenue"], name="Revenue",
                             marker_color="#10C87A", marker_line_width=0, opacity=0.85))
        fig.add_trace(go.Bar(x=m["date"], y=m["total_cost"], name="Cost",
                             marker_color="#E53E4D", marker_line_width=0, opacity=0.85))
        fig.add_trace(go.Scatter(x=m["date"], y=m["gross_margin"], name="Margin",
                                 line=dict(color="#F0A500", width=2),
                                 mode="lines+markers", marker=dict(size=4)))
        fig.update_layout(**dark(height=360, barmode="group",
            legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10))))
        st.plotly_chart(fig, use_container_width=True)

        section_heading("Margin % by plant")
        pm = fin.groupby("plant").agg(rev=("total_revenue","sum"),
                                       cost=("total_cost","sum")).reset_index()
        pm["mp"] = (pm["rev"]-pm["cost"])/pm["rev"]*100
        pm = pm.sort_values("mp")
        fig2 = go.Figure(go.Bar(
            x=pm["mp"], y=pm["plant"], orientation="h",
            marker_color=[PLANT_COLOR.get(p,"#F0A500") for p in pm["plant"]],
            marker_line_width=0,
            text=pm["mp"].apply(lambda v: f"{v:.1f}%"),
            textposition="outside", textfont=dict(size=10, color="#8A94A8")))
        fig2.update_layout(**dark(height=300, showlegend=False,
            xaxis=dict(gridcolor="#1D2235", linecolor="#1D2235",
                       tickfont=dict(size=10, color="#50586A"), ticksuffix="%")))
        st.plotly_chart(fig2, use_container_width=True)

        section_heading("Detail by plant")
        d = fin.groupby("plant").agg(
            Revenue=("total_revenue","sum"),
            Cost=("total_cost","sum"),
            Margin=("gross_margin","sum")).reset_index()
        d["Margin %"] = (d["Margin"]/d["Revenue"]*100).round(1).astype(str) + "%"
        for c in ["Revenue","Cost","Margin"]:
            d[c] = d[c].apply(lambda v: f"€{v:,.0f}")
        st.dataframe(d, use_container_width=True, hide_index=True)


    # ── 05 Maintenance ───────────────────────────────────────────────────────
    elif page == "Maintenance":
        page_header("Operational Planning", "Maintenance Schedule",
                    "Recommended shutdown windows — sequenced for zero supply gap")

        MAINT = [
            {"plant":"Barcelona","last":"2023-08-01","duration":20,"interval_y":2},
            {"plant":"Zaragoza", "last":"2023-06-01","duration":15,"interval_y":3},
            {"plant":"Alicante", "last":"2023-12-01","duration":12,"interval_y":3},
            {"plant":"Gijon",    "last":"2023-10-01","duration":8, "interval_y":3},
            {"plant":"Madrid",   "last":"2025-01-01","duration":22,"interval_y":2},
        ]
        today = pd.Timestamp("2026-06-05")
        rows = []
        for m in MAINT:
            last = pd.Timestamp(m["last"])
            nxt  = last + pd.DateOffset(years=m["interval_y"])
            days = (nxt - today).days
            status = "OVERDUE" if days < 0 else ("DUE SOON" if days < 90 else "OK")
            rows.append({**m, "next": str(nxt.date()), "days": days, "status": status})
        df_m = pd.DataFrame(rows)

        S_COL = {"OVERDUE":"#E53E4D","DUE SOON":"#F07030","OK":"#10C87A"}
        B_CLS = {"OVERDUE":"crit","DUE SOON":"high","OK":"low"}

        k1, k2, k3 = st.columns(3)
        with k1: stat_block("Overdue",     str((df_m["status"]=="OVERDUE").sum()),
                             "schedule immediately",
                             "danger" if (df_m["status"]=="OVERDUE").sum() else "")
        with k2: stat_block("Due soon",    str((df_m["status"]=="DUE SOON").sum()), "within 90 days",
                             "warning" if (df_m["status"]=="DUE SOON").sum() else "")
        with k3: stat_block("On schedule", str((df_m["status"]=="OK").sum()))

        st.markdown("---")
        section_heading("Plant maintenance status")
        mcols = st.columns(len(rows))
        for col, r in zip(mcols, rows):
            c = S_COL[r["status"]]
            badge_cls = B_CLS[r["status"]]
            status_txt = r["status"]
            col.markdown(
                f"<div class='m-plant-card' style='border-top:2px solid {c}'>"
                f"<div class='m-plant-name'>{r['plant']}</div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.6rem;"
                f"color:#374151;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem'>"
                f"next window</div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.82rem;"
                f"font-weight:600;color:{c}'>{r['next']}</div>"
                f"<div style='font-family:IBM Plex Mono,monospace;font-size:0.7rem;"
                f"color:#374151;margin-top:0.25rem'>{r['days']:+d}d · {r['duration']}d shutdown</div>"
                f"<div style='margin-top:0.5rem'>"
                f"<span class='m-badge {badge_cls}'>{status_txt}</span>"
                f"</div></div>", unsafe_allow_html=True)

        st.markdown("---")
        section_heading("Maintenance timeline")
        timeline_data = []
        for r in rows:
            last = pd.Timestamp(r["last"])
            nxt = pd.Timestamp(r["next"])
            timeline_data.append({
                "Plant": r["plant"],
                "Last": last.strftime("%Y-%m-%d"),
                "Next": nxt.strftime("%Y-%m-%d"),
                "Duration": f"{r['duration']}d",
                "Status": r["status"]
            })
        st.dataframe(pd.DataFrame(timeline_data), use_container_width=True, hide_index=True)
        st.markdown(
            "<div style='font-family:IBM Plex Mono,monospace;font-size:0.72rem;"
            "color:#374151'>⬡ No two plants in the same supply zone may shut down "
            "within 60 days of each other.</div>", unsafe_allow_html=True)


    # ── 06 Demand Forecast ───────────────────────────────────────────────────
    elif page == "Demand Forecast":
        page_header("Predictive Analytics", "18-Month Demand Forecast",
                    "LOX consumption trend · network capacity · supply headroom")

        cons = load_consumption()
        total = cons.groupby("date")["daily_consumption_tons"].sum().reset_index().sort_values("date")
        total["x"] = (total["date"] - total["date"].min()).dt.days
        coeffs = np.polyfit(total["x"], total["daily_consumption_tons"], 1)
        poly = np.poly1d(coeffs)
        ld, lx = total["date"].max(), total["x"].max()
        fut_dates = pd.date_range(ld + timedelta(1), periods=548)
        fut_vals  = poly(np.arange(lx+1, lx+549))

        avg_now = total["daily_consumption_tons"].tail(30).mean()
        avg_18  = fut_vals[-30:].mean()
        growth  = (avg_18/avg_now - 1)*100

        k1, k2, k3 = st.columns(3)
        with k1: stat_block("Current demand",  f"{avg_now:.3f}t", "tons/day avg (30d)")
        with k2: stat_block("Forecast (18mo)", f"{avg_18:.3f}t",  "tons/day avg")
        with k3: stat_block("Growth",          f"+{growth:.1f}%", "over 18 months")

        st.markdown("---")
        section_heading("Historical + 18-month forecast")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=list(fut_dates)+list(fut_dates[::-1]),
            y=list(fut_vals*1.1)+list(fut_vals[::-1]*0.9),
            fill="toself", fillcolor="rgba(240,165,0,0.04)",
            line=dict(color="rgba(0,0,0,0)"), showlegend=False))
        fig.add_trace(go.Scatter(
            x=total["date"], y=total["daily_consumption_tons"],
            mode="lines", name="Historical",
            line=dict(color="#18A8C8", width=1.5), opacity=0.8))
        fig.add_trace(go.Scatter(
            x=fut_dates, y=fut_vals,
            mode="lines", name="Forecast",
            line=dict(color="#F0A500", width=2, dash="dash")))
        fig.update_layout(**dark(height=400,
            legend=dict(orientation="h", y=1.05, x=0, bgcolor="rgba(0,0,0,0)",
                        font=dict(size=10))))
        st.plotly_chart(fig, use_container_width=True)

        section_heading("Capacity vs demand scenarios")
        prod = load_production()
        cap = prod.groupby("plant")["production_tons"].mean().sum()
        sc = pd.DataFrame({
            "Scenario": ["Full network","One plant in maintenance","Two plants down"],
            "Capacity (t/d)": [f"{cap:.2f}", f"{cap*0.8:.2f}", f"{cap*0.6:.2f}"],
            "Demand (t/d)":   [f"{avg_18:.3f}"]*3,
            "Headroom": [f"+{(cap/avg_18-1)*100:.0f}%",
                         f"+{(cap*0.8/avg_18-1)*100:.0f}%",
                         f"{(cap*0.6/avg_18-1)*100:.0f}%"],
        })
        st.dataframe(sc, use_container_width=True, hide_index=True)


    # ── 07 AI Copilot ────────────────────────────────────────────────────────
    elif page == "AI Copilot":
        page_header("Momentum Intelligence", "AI Copilot",
                    "Ask anything — risk · operations · finance · maintenance")

        api_key = os.environ.get("ANTHROPIC_API_KEY","")
        if not api_key:
            st.markdown(
                "<div class='m-alert crit'><div class='m-alert-dot'></div>"
                "<div class='m-alert-body'>"
                "<div class='m-alert-name'>API key required</div>"
                "<div class='m-alert-detail'>Set <strong>ANTHROPIC_API_KEY</strong> "
                "and restart</div></div></div>", unsafe_allow_html=True)
            st.stop()

        from anthropic import Anthropic

        STARTERS = [
            "Morning briefing — which hospitals are at risk today?",
            "Which plants need maintenance and in what order?",
            "What is our financial exposure this quarter?",
            "Are there critical alerts requiring immediate action?",
            "What happens to supply if Barcelona shuts down next month?",
        ]

        section_heading("Starter queries")
        s_cols = st.columns(len(STARTERS))
        clicked = None
        for col, q in zip(s_cols, STARTERS):
            if col.button(q[:36]+"…", key=f"sq_{q[:10]}", use_container_width=True):
                clicked = q

        st.markdown("---")
        section_heading("Conversation")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f"<div class='m-chat-label'>You</div>"
                            f"<div class='m-chat-user'>{msg['content']}</div>",
                            unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='m-chat-label'>Momentum AI Copilot</div>"
                            f"<div class='m-chat-ai'>{msg['content']}</div>",
                            unsafe_allow_html=True)

        query = clicked or st.chat_input("Ask the Copilot…")

        if query:
            st.session_state.messages.append({"role":"user","content":query})
            st.markdown(f"<div class='m-chat-label'>You</div>"
                        f"<div class='m-chat-user'>{query}</div>",
                        unsafe_allow_html=True)

            # Tool functions
            s = latest_risk_snapshot()
            crit = s[s["risk_level"]=="CRITICAL"]
            high_s = s[s["risk_level"]=="HIGH"]

            def get_dryout_risk_summary(days_ahead=7):
                return {"critical": crit[["hospital_name","hospital_city","fill_pct","days_to_dryout"]].to_dict("records"),
                        "high": high_s[["hospital_name","hospital_city","fill_pct","days_to_dryout"]].to_dict("records")}
            def get_critical_alerts():
                return {"count":len(crit),"alerts":[{"hospital":r["hospital_name"],
                        "city":r["hospital_city"],"fill_pct":round(r["fill_pct"]*100,1),
                        "days_to_dryout":round(r["days_to_dryout"],1)} for _,r in crit.iterrows()]}
            def get_financial_summary(months=3):
                fin = load_financial()
                bp = fin.groupby("plant").agg(rev=("total_revenue","sum"),cost=("total_cost","sum")).reset_index()
                bp["margin_pct"] = (bp["rev"]-bp["cost"])/bp["rev"]*100
                return {"by_plant":bp.round(2).to_dict("records")}
            def get_maintenance_schedule():
                t = pd.Timestamp.now().normalize()
                M=[{"plant":"Barcelona","last":"2023-08-01","duration":20,"interval_y":2},
                   {"plant":"Zaragoza","last":"2023-06-01","duration":15,"interval_y":3},
                   {"plant":"Alicante","last":"2023-12-01","duration":12,"interval_y":3},
                   {"plant":"Gijon","last":"2023-10-01","duration":8,"interval_y":3},
                   {"plant":"Madrid","last":"2025-01-01","duration":22,"interval_y":2}]
                out=[]
                for m in M:
                    nxt=pd.Timestamp(m["last"])+pd.DateOffset(years=m["interval_y"])
                    d=(nxt-t).days
                    out.append({**m,"next":str(nxt.date()),"days_until":d,
                                "status":"OVERDUE" if d<0 else("DUE_SOON" if d<90 else"OK")})
                return {"schedule":out}
            def get_production_summary():
                pr=load_production()
                l30=pr[pr["date"]>=pr["date"].max()-timedelta(30)]
                s2=l30.groupby("plant").agg(avg=("production_tons","mean"),util=("utilisation_pct","mean")).reset_index()
                return {"summary":s2.round(3).to_dict("records")}

            TOOLS=[
                {"name":"get_dryout_risk_summary","description":"Hospital fill levels and risk","input_schema":{"type":"object","properties":{"days_ahead":{"type":"integer","default":7}}}},
                {"name":"get_critical_alerts","description":"Hospitals below minimum fill","input_schema":{"type":"object","properties":{}}},
                {"name":"get_financial_summary","description":"Revenue, cost, margin by plant","input_schema":{"type":"object","properties":{"months":{"type":"integer","default":3}}}},
                {"name":"get_maintenance_schedule","description":"Plant maintenance windows","input_schema":{"type":"object","properties":{}}},
                {"name":"get_production_summary","description":"Plant production last 30 days","input_schema":{"type":"object","properties":{}}},
            ]
            FNS={"get_dryout_risk_summary":get_dryout_risk_summary,"get_critical_alerts":get_critical_alerts,
                 "get_financial_summary":get_financial_summary,"get_maintenance_schedule":get_maintenance_schedule,
                 "get_production_summary":get_production_summary}
            SYSTEM="""You are the Momentum AI Copilot for ManOxCo's Oxygen Reliability Platform.
Reason across production, logistics, consumption, and finance simultaneously.
Always check critical alerts first. Grade: [URGENT]/[HIGH]/[MEDIUM]/[LOW].
End every response with a concrete action. Be concise. Use **bold** for key numbers."""

            client = Anthropic(api_key=api_key)
            msgs = [{"role":"user","content":query}]

            with st.spinner(""):
                for _ in range(6):
                    resp = client.messages.create(
                        model="claude-sonnet-4-6", max_tokens=1024,
                        system=SYSTEM, tools=TOOLS, messages=msgs)
                    if resp.stop_reason == "end_turn":
                        answer = " ".join(b.text for b in resp.content if hasattr(b,"text"))
                        break
                    if resp.stop_reason == "tool_use":
                        msgs.append({"role":"assistant","content":resp.content})
                        results=[]
                        for b in resp.content:
                            if b.type=="tool_use":
                                fn=FNS.get(b.name,lambda **kw:{"error":"unknown"})
                                results.append({"type":"tool_result","tool_use_id":b.id,
                                                "content":json.dumps(fn(**b.input),default=str)})
                        msgs.append({"role":"user","content":results})
                else:
                    answer = "Unable to complete. Please try again."

            st.session_state.messages.append({"role":"assistant","content":answer})
            st.markdown(f"<div class='m-chat-label'>Momentum AI Copilot</div>"
                        f"<div class='m-chat-ai'>{answer}</div>",
                        unsafe_allow_html=True)
            st.rerun()
