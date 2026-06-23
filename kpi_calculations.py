"""
kpi_calculations.py — All KPI computations for Kalshiyaa Traders
"""
from data_cleaning import load_and_clean, monthly_summary, kpi_summary
import pandas as pd, numpy as np

def full_kpi_report():
    df = load_and_clean()
    monthly = monthly_summary(df)
    kpis = kpi_summary(df, monthly)

    print("=" * 60)
    print("   KALSHIYAA TRADERS — CFO KPI REPORT")
    print("   Period: Apr 2025 – Mar 2026")
    print("=" * 60)

    fmt = lambda v: f"₹{v:>15,.2f}"
    print(f"\n{'LIQUIDITY':}")
    print(f"  Total Credits        {fmt(kpis['total_credits'])}")
    print(f"  Total Debits         {fmt(kpis['total_debits'])}")
    print(f"  Net Cash Flow        {fmt(kpis['net_cash_flow'])}")
    print(f"  Opening Balance      {fmt(kpis['opening_balance'])}")
    print(f"  Closing Balance      {fmt(kpis['closing_balance'])}")
    print(f"  Average Balance      {fmt(kpis['avg_balance'])}")
    print(f"  Min Balance          {fmt(kpis['min_balance'])}")
    print(f"  Max Balance          {fmt(kpis['max_balance'])}")

    print(f"\n{'EFFICIENCY':}")
    print(f"  Avg Monthly Burn     {fmt(kpis['avg_monthly_burn'])}")
    print(f"  Savings Rate         {kpis['savings_rate_pct']:>18.2f}%")
    print(f"  Liquidity Ratio      {kpis['liquidity_ratio']:>18.2f}x")
    print(f"  Runway (months)      {kpis['runway_months']:>18.2f}")
    print(f"  Health Score         {kpis['financial_health_score']:>18.0f}/100")
    print(f"  Total Transactions   {kpis['total_transactions']:>18,}")

    print(f"\n{'TOP VENDORS BY OUTFLOW':}")
    top_out = df.groupby("Party_Name")["Withdrawal"].sum().sort_values(ascending=False).head(10)
    for p, v in top_out.items():
        print(f"  {p:<45} {fmt(v)}")

    print(f"\n{'TOP INCOME SOURCES':}")
    top_in = df.groupby("Party_Name")["Deposit"].sum().sort_values(ascending=False).head(10)
    for p, v in top_in.items():
        print(f"  {p:<45} {fmt(v)}")

    return kpis, monthly, df

if __name__ == "__main__":
    full_kpi_report()
