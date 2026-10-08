"""Generate reproducible synthetic e-commerce data for portfolio analysis."""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)


def main(n_transactions: int = 50_000, n_customers: int = 8_000, seed: int = 42):
    rng = np.random.default_rng(seed)
    start = np.datetime64("2024-01-01")
    end = np.datetime64("2025-12-31")
    day_offsets = rng.integers(
        0, int((end - start).astype("timedelta64[D]").astype(int)) + 1,
        n_transactions
    )
    dates = pd.to_datetime(start + day_offsets.astype("timedelta64[D]"))
    customer_ids = [f"C{i:05d}" for i in range(1, n_customers + 1)]
    product_ids = [f"P{i:03d}" for i in range(1, 81)]
    categories = ["Electronics", "Home & Kitchen", "Fashion", "Beauty", "Sports", "Books"]
    cat_probs = np.array([0.18, 0.20, 0.22, 0.15, 0.13, 0.12])
    product_cat = rng.choice(categories, size=len(product_ids), p=cat_probs)
    price_ranges = {
        "Electronics": (500, 35000), "Home & Kitchen": (150, 9000),
        "Fashion": (199, 6000), "Beauty": (99, 2500),
        "Sports": (250, 12000), "Books": (99, 1800)
    }
    product_rows = []
    for pid, cat in zip(product_ids, product_cat):
        lo, hi = price_ranges[cat]
        product_rows.append((
            pid, f"{cat.split()[0]} Product {pid[-3:]}", cat,
            round(float(rng.uniform(lo, hi)), 2)
        ))
    products = pd.DataFrame(
        product_rows, columns=["product_id", "product_name", "category", "list_price"]
    )
    products.to_csv(DATA / "products.csv", index=False)

    regions = ["North", "South", "East", "West", "Central"]
    customer_rows = []
    for cid in customer_ids:
        signup = pd.Timestamp("2023-01-01") + pd.Timedelta(
            days=int(rng.integers(0, 730))
        )
        customer_rows.append((
            cid, str(signup.date()), rng.choice(regions),
            rng.choice(["18-24", "25-34", "35-44", "45-54", "55+"]),
            rng.choice(["F", "M", "Prefer not to say"], p=[0.48, 0.48, 0.04])
        ))
    customers = pd.DataFrame(
        customer_rows,
        columns=["customer_id", "signup_date", "region", "age_group", "gender"]
    )
    customers.to_csv(DATA / "customers.csv", index=False)

    # Weighted customer selection creates repeat purchasing behaviour.
    weights = rng.lognormal(mean=0.0, sigma=1.0, size=n_customers)
    weights = weights / weights.sum()
    chosen_customers = rng.choice(customer_ids, size=n_transactions, p=weights)
    chosen_product_idx = rng.integers(0, len(products), n_transactions)
    chosen_products = products.iloc[chosen_product_idx].reset_index(drop=True)
    qty = rng.choice([1, 2, 3, 4], size=n_transactions, p=[0.70, 0.20, 0.08, 0.02])
    discount = rng.choice(
        [0.0, 0.05, 0.10, 0.15, 0.20, 0.25], size=n_transactions,
        p=[0.30, 0.16, 0.24, 0.15, 0.10, 0.05]
    )
    channels = rng.choice(
        ["Website", "Mobile App", "Marketplace"], size=n_transactions,
        p=[0.35, 0.40, 0.25]
    )
    order_ids = [f"O{i:06d}" for i in range(1, n_transactions + 1)]
    transactions = pd.DataFrame({
        "transaction_id": [f"T{i:07d}" for i in range(1, n_transactions + 1)],
        "order_id": order_ids,
        "order_date": dates,
        "customer_id": chosen_customers,
        "product_id": chosen_products["product_id"],
        "quantity": qty,
        "unit_price": chosen_products["list_price"].to_numpy(),
        "discount_pct": discount,
        "channel": channels,
        "payment_method": rng.choice(
            ["UPI", "Card", "Net Banking", "COD", "Wallet"], size=n_transactions
        )
    })

    # Add a small amount of realistic data-quality issues for cleaning practice.
    if n_transactions >= 100:
        missing_idx = rng.choice(
            transactions.index, size=max(1, n_transactions // 1000), replace=False
        )
        transactions.loc[missing_idx, "channel"] = np.nan
        transactions = pd.concat([transactions, transactions.iloc[:5]], ignore_index=True)
    transactions.to_csv(DATA / "ecommerce_transactions.csv", index=False)
    print(
        f"Created {len(transactions):,} raw transaction rows, "
        f"{len(customers):,} customers, {len(products):,} products in {DATA}"
    )


if __name__ == "__main__":
    main()
