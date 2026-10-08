"""Clean, analyze, visualize, and export e-commerce analytics tables."""
from pathlib import Path
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs"
FIG = OUT / "figures"
OUT.mkdir(exist_ok=True)
FIG.mkdir(exist_ok=True)


def main():
    tx = pd.read_csv(DATA / "ecommerce_transactions.csv", parse_dates=["order_date"])
    customers = pd.read_csv(DATA / "customers.csv", parse_dates=["signup_date"])
    products = pd.read_csv(DATA / "products.csv")

    raw_rows = len(tx)
    raw_unique_ids = tx["transaction_id"].nunique()
    tx = tx.drop_duplicates(subset=["transaction_id"])
    duplicate_ids_removed = raw_rows - len(tx)

    tx["order_date"] = pd.to_datetime(tx["order_date"], errors="coerce")
    tx["quantity"] = pd.to_numeric(tx["quantity"], errors="coerce")
    tx["unit_price"] = pd.to_numeric(tx["unit_price"], errors="coerce")
    tx["discount_pct"] = pd.to_numeric(tx["discount_pct"], errors="coerce")
    tx = tx.dropna(subset=["order_date", "customer_id", "product_id", "quantity", "unit_price"])
    tx = tx[(tx["quantity"] > 0) & (tx["unit_price"] >= 0)]
    tx["discount_pct"] = tx["discount_pct"].fillna(0).clip(0, 1)
    tx["channel"] = tx["channel"].fillna("Unknown")
    tx["gross_sales"] = tx["quantity"] * tx["unit_price"]
    tx["discount_amount"] = tx["gross_sales"] * tx["discount_pct"]
    tx["revenue"] = tx["gross_sales"] - tx["discount_amount"]
    tx["order_month"] = tx["order_date"].dt.to_period("M").astype(str)
    tx["order_year"] = tx["order_date"].dt.year
    tx["order_quarter"] = "Q" + tx["order_date"].dt.quarter.astype(str)
    tx["weekday"] = tx["order_date"].dt.day_name()

    tx = tx.merge(
        products[["product_id", "product_name", "category"]],
        on="product_id", how="left", validate="many_to_one"
    )
    tx = tx.merge(
        customers[["customer_id", "region", "age_group", "gender"]],
        on="customer_id", how="left", validate="many_to_one"
    )
    tx["category"] = tx["category"].fillna("Unknown")
    tx["region"] = tx["region"].fillna("Unknown")

    order_count = tx["order_id"].nunique()
    customer_count = tx["customer_id"].nunique()
    total_revenue = tx["revenue"].sum()
    total_units = tx["quantity"].sum()
    repeat_customers = (tx.groupby("customer_id")["order_id"].nunique() > 1).sum()
    kpis = pd.DataFrame([
        ("Raw rows", raw_rows),
        ("Clean transaction rows", len(tx)),
        ("Distinct orders", order_count),
        ("Active customers", customer_count),
        ("Total revenue", round(total_revenue, 2)),
        ("Units sold", int(total_units)),
        ("Average order value", round(total_revenue / order_count, 2) if order_count else 0),
        ("Repeat customers", int(repeat_customers)),
        ("Repeat customer rate (%)", round(repeat_customers / customer_count * 100, 2) if customer_count else 0),
        ("Duplicate transaction IDs removed", duplicate_ids_removed),
    ], columns=["metric", "value"])
    kpis.to_csv(OUT / "kpi_summary.csv", index=False)

    monthly = tx.groupby("order_month", as_index=False).agg(
        revenue=("revenue", "sum"), orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"), customers=("customer_id", "nunique")
    )
    monthly.to_csv(OUT / "monthly_sales.csv", index=False)

    category = tx.groupby("category", as_index=False).agg(
        revenue=("revenue", "sum"), units_sold=("quantity", "sum"),
        orders=("order_id", "nunique"), avg_discount_pct=("discount_pct", "mean")
    ).sort_values("revenue", ascending=False)
    category.to_csv(OUT / "category_sales.csv", index=False)

    top_products = tx.groupby(
        ["product_id", "product_name", "category"], as_index=False
    ).agg(
        revenue=("revenue", "sum"), units_sold=("quantity", "sum"),
        orders=("order_id", "nunique")
    ).sort_values("revenue", ascending=False).head(15)
    top_products.to_csv(OUT / "top_products.csv", index=False)

    customer_metrics = tx.groupby("customer_id", as_index=False).agg(
        orders=("order_id", "nunique"), revenue=("revenue", "sum"),
        units=("quantity", "sum"), last_order=("order_date", "max"),
        first_order=("order_date", "min")
    )
    snapshot = tx["order_date"].max() + pd.Timedelta(days=1)
    customer_metrics["recency_days"] = (snapshot - customer_metrics["last_order"]).dt.days
    customer_metrics["tenure_days"] = (
        customer_metrics["last_order"] - customer_metrics["first_order"]
    ).dt.days
    q_freq = customer_metrics["orders"].quantile([0.33, 0.66]).to_list()
    q_money = customer_metrics["revenue"].quantile([0.33, 0.66]).to_list()

    def segment(row):
        if (
            row["orders"] >= q_freq[1]
            and row["revenue"] >= q_money[1]
            and row["recency_days"] <= customer_metrics["recency_days"].median()
        ):
            return "High Value"
        if row["orders"] >= q_freq[1]:
            return "Loyal / Repeat"
        if row["recency_days"] > customer_metrics["recency_days"].quantile(0.75):
            return "At Risk / Inactive"
        return "Regular"

    customer_metrics["segment"] = customer_metrics.apply(segment, axis=1)
    customer_metrics.to_csv(OUT / "customer_metrics.csv", index=False)
    segments = customer_metrics.groupby("segment", as_index=False).agg(
        customers=("customer_id", "nunique"), revenue=("revenue", "sum"),
        avg_customer_revenue=("revenue", "mean"), avg_orders=("orders", "mean")
    ).sort_values("revenue", ascending=False)
    segments.to_csv(OUT / "customer_segments.csv", index=False)

    customer_order_counts = tx.groupby("customer_id")["order_id"].nunique()
    retention = pd.DataFrame([
        ("Customers with 1 order", int((customer_order_counts == 1).sum())),
        ("Customers with 2+ orders", int((customer_order_counts >= 2).sum())),
        ("Repeat customer rate (%)", round((customer_order_counts >= 2).mean() * 100, 2)),
        ("Average orders per customer", round(customer_order_counts.mean(), 2))
    ], columns=["metric", "value"])
    retention.to_csv(OUT / "retention_summary.csv", index=False)

    # Charts
    plt.figure(figsize=(11, 5))
    plt.plot(monthly["order_month"], monthly["revenue"], marker="o")
    plt.title("Monthly Revenue Trend")
    plt.xlabel("Month")
    plt.ylabel("Revenue")
    plt.xticks(rotation=60, ha="right")
    plt.tight_layout()
    plt.savefig(FIG / "monthly_revenue.png", dpi=160)
    plt.close()

    plt.figure(figsize=(9, 5))
    plot_cat = category.sort_values("revenue")
    plt.barh(plot_cat["category"], plot_cat["revenue"])
    plt.title("Revenue by Product Category")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig(FIG / "category_revenue.png", dpi=160)
    plt.close()

    plt.figure(figsize=(10, 5))
    top = top_products.sort_values("revenue")
    plt.barh(top["product_name"], top["revenue"])
    plt.title("Top 15 Products by Revenue")
    plt.xlabel("Revenue")
    plt.tight_layout()
    plt.savefig(FIG / "top_products.png", dpi=160)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(customer_metrics["revenue"], bins=40)
    plt.title("Customer Revenue Distribution")
    plt.xlabel("Revenue per customer")
    plt.ylabel("Customer count")
    plt.tight_layout()
    plt.savefig(FIG / "customer_revenue_distribution.png", dpi=160)
    plt.close()

    db_path = OUT / "ecommerce_analytics.db"
    with sqlite3.connect(db_path) as con:
        tx.to_sql("transactions", con, if_exists="replace", index=False)
        customers.to_sql("customers", con, if_exists="replace", index=False)
        products.to_sql("products", con, if_exists="replace", index=False)
        customer_metrics.to_sql("customer_metrics", con, if_exists="replace", index=False)

    print("Analysis complete.")
    print(kpis.to_string(index=False))
    print(f"Tables and charts saved to: {OUT}")


if __name__ == "__main__":
    main()
