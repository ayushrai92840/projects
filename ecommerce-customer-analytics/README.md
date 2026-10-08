# E-Commerce Customer Analytics

Portfolio-ready analytics project using **Python, Pandas, NumPy, Matplotlib, SQL, and Power BI**.

> **Dataset notice:** All records and business metrics in this project are synthetic and for learning/portfolio demonstration only. They do not describe a real company.

## Business questions
- What are revenue, orders, units sold, and average order value?
- Which categories and products contribute most revenue?
- How do sales change month to month?
- What percentage of customers make repeat purchases?
- Which customer groups may benefit from targeted campaigns?

## Repository structure
```text
ecommerce-customer-analytics/
├── data/                  # generated CSV data (created by script)
├── outputs/               # analysis tables and charts (created by script)
├── powerbi/measures.dax   # starter DAX measures
├── reports/               # case study and resume wording
├── sql/                   # reusable SQL analysis queries
├── src/                   # data generation and analysis pipeline
├── notebooks/README.md
├── requirements.txt
└── README.md
```

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/generate_data.py
python src/analyze.py
```

The generator creates 50,000 transaction rows plus customer and product tables. The analysis script cleans duplicates and missing values, engineers revenue/time features, exports KPI/category/monthly/product/customer summaries, creates charts, and writes a local SQLite database to `outputs/`.

## Power BI
Run the Python scripts, then import CSVs from `outputs/` into Power BI Desktop. Suggested report pages: Executive Overview, Product Performance, Customer Insights, and Retention & Trends. Starter measures are in `powerbi/measures.dax`.

## Metric definitions
- **Revenue:** quantity × unit price × (1 − discount percentage).
- **AOV:** total revenue / distinct orders.
- **Repeat customer rate:** customers with more than one order / active customers.
- **Customer segments:** illustrative rule-based groups, not a validated marketing model.

## Limitations
Revenue is not profit: product costs, shipping, refunds, and marketing spend are not included. Repeat purchase rate is not cohort retention. Treat recommendations as hypotheses and do not claim measured business impact from this synthetic dataset.

## License
MIT. See `LICENSE`.
