"""
eda.py — Exploratory Data Analysis for Kalshiyaa Traders
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from data_cleaning import load_and_clean, monthly_summary

COLORS = {"primary": "#2563EB", "success": "#10B981",
          "warning": "#F59E0B", "danger": "#EF4444",
          "purple": "#8B5CF6", "gray": "#6B7280"}

def run_eda():
    df = load_and_clean()
    monthly = monthly_summary(df)

    # 1. Monthly Cash Flow Waterfall
    fig1 = go.Figure(go.Waterfall(
        name="Net Cash Flow",
        orientation="v",
        measure=["relative"] * len(monthly),
        x=monthly["MonthLabel"],
        y=monthly["NetCashFlow"],
        connector={"line": {"color": "#888"}},
        increasing={"marker": {"color": COLORS["success"]}},
        decreasing={"marker": {"color": COLORS["danger"]}},
        totals={"marker": {"color": COLORS["primary"]}},
        text=[f"₹{v:,.0f}" for v in monthly["NetCashFlow"]],
        textposition="outside",
    ))
    fig1.update_layout(title="Monthly Net Cash Flow (Waterfall)", template="plotly_white",
                       font=dict(family="Segoe UI"), height=450)
    fig1.write_html("outputs/eda_waterfall.html")

    # 2. Credits vs Debits Bar
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(name="Credits", x=monthly["MonthLabel"], y=monthly["Credits"],
                          marker_color=COLORS["success"], text=[f"₹{v/1e5:.1f}L" for v in monthly["Credits"]], textposition="auto"))
    fig2.add_trace(go.Bar(name="Debits",  x=monthly["MonthLabel"], y=monthly["Debits"],
                          marker_color=COLORS["danger"],  text=[f"₹{v/1e5:.1f}L" for v in monthly["Debits"]],  textposition="auto"))
    fig2.update_layout(barmode="group", title="Monthly Credits vs Debits",
                       template="plotly_white", font=dict(family="Segoe UI"), height=450)
    fig2.write_html("outputs/eda_credits_debits.html")

    # 3. Balance Trend
    fig3 = px.area(df, x="Date", y="Balance",
                   title="Running Balance Trend",
                   labels={"Balance":"Balance (₹)"},
                   color_discrete_sequence=[COLORS["primary"]])
    fig3.update_layout(template="plotly_white", font=dict(family="Segoe UI"), height=400)
    fig3.write_html("outputs/eda_balance_trend.html")

    # 4. Payment Mode Distribution
    mode_grp = df.groupby("Payment_Mode").agg(
        Txns=("Date","count"),
        Volume=("NetAmount","sum")
    ).reset_index().sort_values("Txns", ascending=False)
    fig4 = px.bar(mode_grp, x="Payment_Mode", y="Txns", color="Payment_Mode",
                  title="Transaction Count by Payment Mode",
                  labels={"Txns":"Transactions","Payment_Mode":"Mode"},
                  text="Txns")
    fig4.update_layout(showlegend=False, template="plotly_white",
                       font=dict(family="Segoe UI"), height=400)
    fig4.write_html("outputs/eda_payment_modes.html")

    # 5. Category Expense Treemap
    cat_debit = df[df["Withdrawal"]>0].groupby("Category")["Withdrawal"].sum().reset_index()
    fig5 = px.treemap(cat_debit, path=["Category"], values="Withdrawal",
                      title="Expense Categories (Treemap)",
                      color="Withdrawal", color_continuous_scale="Reds")
    fig5.update_layout(font=dict(family="Segoe UI"), height=500)
    fig5.write_html("outputs/eda_expense_treemap.html")

    # 6. Top 15 Vendors (Outflow)
    top_vendors = df.groupby("Party_Name")["Withdrawal"].sum().sort_values(ascending=False).head(15).reset_index()
    fig6 = px.bar(top_vendors, x="Withdrawal", y="Party_Name", orientation="h",
                  title="Top 15 Expense Vendors",
                  color="Withdrawal", color_continuous_scale="Reds",
                  text=[f"₹{v/1e5:.1f}L" for v in top_vendors["Withdrawal"]])
    fig6.update_layout(yaxis={"autorange":"reversed"}, template="plotly_white",
                       font=dict(family="Segoe UI"), height=550)
    fig6.write_html("outputs/eda_top_vendors.html")

    print("EDA charts saved to outputs/")

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    run_eda()
