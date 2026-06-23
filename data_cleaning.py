"""
data_cleaning.py
Kalshiyaa Traders — CFO Financial Analytics Platform
"""
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def load_and_clean(filepath: str = "data/kalshst_bank_statement_parsed.csv") -> pd.DataFrame:
    df = pd.read_csv(filepath, encoding="latin1")
    df.columns = ["Date", "Particulars", "Payment_Mode", "Party_Name",
                  "Ref_Number", "Withdrawal", "Deposit", "Balance"]

    # Drop blank rows
    df.dropna(subset=["Balance"], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], format="%m/%d/%Y", errors="coerce")
    df.dropna(subset=["Date"], inplace=True)
    df.sort_values("Date", inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Numeric
    df["Withdrawal"] = pd.to_numeric(df["Withdrawal"], errors="coerce").fillna(0)
    df["Deposit"]    = pd.to_numeric(df["Deposit"],    errors="coerce").fillna(0)
    df["Balance"]    = pd.to_numeric(df["Balance"],    errors="coerce")

    # Derived
    df["Month"]       = df["Date"].dt.to_period("M").astype(str)
    df["MonthLabel"]  = df["Date"].dt.strftime("%b %Y")
    df["Quarter"]     = df["Date"].dt.to_period("Q").astype(str)
    df["WeekDay"]     = df["Date"].dt.day_name()
    df["IsCredit"]    = df["Deposit"] > 0
    df["IsDebit"]     = df["Withdrawal"] > 0
    df["NetAmount"]   = df["Deposit"] - df["Withdrawal"]

    # Categorise payment modes
    credit_modes = {"IMPSAB","NEFT","RTGS","UPI","CREDIT OF","NACH","TRANSFER","CLG","CHEQUE"}
    df["TxnType"] = np.where(df["Deposit"] > 0, "Credit", "Debit")

    # Vendor category tagging
    vendor_map = {
        "GOOGLE": "Digital Services",
        "RAJALAKSHMI": "Suppliers",
        "ASHRE": "Suppliers",
        "VMS": "Suppliers",
        "JSS": "Suppliers",
        "STEEL": "Raw Materials",
        "REGISTRATION": "Government / Statutory",
        "CONSTRUCTIONS": "Real Estate",
        "HOMES": "Real Estate",
        "ESTATES": "Real Estate",
        "PROMOTERS": "Real Estate",
        "ENTERPRISES": "Trade Vendors",
        "AGENCIES": "Trade Vendors",
        "BANK": "Banking",
        "LOAN": "Banking",
        "SELF": "Internal Transfer",
        "TRANSFER": "Internal Transfer",
        "INSUFFICIENT": "Returned / Bounced",
        "REJECT": "Returned / Bounced",
    }
    def tag_category(name: str) -> str:
        if not isinstance(name, str):
            return "Uncategorised"
        name_up = name.upper()
        for kw, cat in vendor_map.items():
            if kw in name_up:
                return cat
        return "Other"

    df["Category"] = df["Party_Name"].apply(tag_category)
    return df


def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("Month").agg(
        Credits    =("Deposit",    "sum"),
        Debits     =("Withdrawal", "sum"),
        Txns       =("Date",       "count"),
        OpenBal    =("Balance",    "first"),
        CloseBal   =("Balance",    "last"),
        MonthLabel =("MonthLabel", "first"),
    ).reset_index()
    grp["NetCashFlow"] = grp["Credits"] - grp["Debits"]
    grp["BurnRate"]    = grp["Debits"]
    grp["SavingsRate"] = np.where(grp["Credits"] > 0,
                                  (grp["NetCashFlow"] / grp["Credits"]) * 100, 0)
    return grp.sort_values("Month")


def kpi_summary(df: pd.DataFrame, monthly: pd.DataFrame) -> dict:
    total_credits = df["Deposit"].sum()
    total_debits  = df["Withdrawal"].sum()
    net_cf        = total_credits - total_debits
    avg_balance   = df["Balance"].mean()
    min_balance   = df["Balance"].min()
    max_balance   = df["Balance"].max()
    opening_bal   = df.sort_values("Date").iloc[0]["Balance"]
    closing_bal   = df.sort_values("Date").iloc[-1]["Balance"]
    burn_rate     = monthly["Debits"].mean()
    savings_rate  = (net_cf / total_credits * 100) if total_credits > 0 else 0
    runway_months = (closing_bal / burn_rate) if burn_rate > 0 else 0
    liquidity_ratio = (total_credits / total_debits) if total_debits > 0 else 0

    # Financial health score (0-100)
    score = 50
    if savings_rate > 10: score += 15
    elif savings_rate > 0: score += 5
    else: score -= 15
    if liquidity_ratio >= 1.1: score += 15
    elif liquidity_ratio >= 1.0: score += 5
    else: score -= 20
    if runway_months >= 3: score += 10
    elif runway_months >= 1: score += 5
    else: score -= 10
    if min_balance > 0: score += 10
    score = max(0, min(100, score))

    return {
        "total_credits": total_credits,
        "total_debits": total_debits,
        "net_cash_flow": net_cf,
        "avg_balance": avg_balance,
        "min_balance": min_balance,
        "max_balance": max_balance,
        "opening_balance": opening_bal,
        "closing_balance": closing_bal,
        "avg_monthly_burn": burn_rate,
        "savings_rate_pct": savings_rate,
        "liquidity_ratio": liquidity_ratio,
        "runway_months": runway_months,
        "financial_health_score": score,
        "total_transactions": len(df),
    }


if __name__ == "__main__":
    df = load_and_clean()
    monthly = monthly_summary(df)
    kpis = kpi_summary(df, monthly)
    print("=== KPI Summary ===")
    for k, v in kpis.items():
        print(f"  {k}: {v:,.2f}" if isinstance(v, float) else f"  {k}: {v}")
    print("\n=== Monthly Cash Flow ===")
    print(monthly[["MonthLabel","Credits","Debits","NetCashFlow","SavingsRate"]].to_string(index=False))
