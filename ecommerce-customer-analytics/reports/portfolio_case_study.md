# Portfolio Case Study: E-Commerce Customer Analytics

## Objective
Build a repeatable analytics workflow to explore sales, product performance, customer purchasing patterns, and repeat purchasing using Python, SQL, and Power BI.

## Dataset
The project generator creates 50,000 transaction lines plus customer and product dimensions. Data is synthetic and includes a small number of deliberate quality issues for practice. Clearly label it as synthetic in the portfolio.

## Workflow
1. Generate data with a fixed random seed.
2. Inspect and clean duplicate transaction IDs, missing values, invalid quantities, and numeric types.
3. Engineer revenue, discount amount, month, year, quarter, and weekday features.
4. Analyze monthly sales, category performance, top products, customer value, and repeat purchasing.
5. Export clean KPI tables and visualizations.
6. Load outputs into Power BI and create an interactive dashboard.
7. Use SQL queries to validate metrics and answer business questions.

## Business questions and actions to consider
- **Category performance:** compare revenue and units to plan stock levels by category.
- **Product performance:** investigate high-revenue products for availability and margin; revenue alone is not profit.
- **Seasonality:** use monthly patterns to plan campaigns and inventory, while checking whether trends persist across years.
- **Customer segments:** test targeted loyalty or win-back campaigns on high-value, repeat, and inactive customers.
- **Channel mix:** compare channel revenue and order count, then consider conversion rate and acquisition cost if those data become available.

## Results
Run the pipeline and review the generated files:
- Total revenue, order count, average order value, and repeat customer rate: `outputs/kpi_summary.csv`
- Highest-revenue category: `outputs/category_sales.csv`
- Highest-revenue products: `outputs/top_products.csv`
- Monthly trend: `outputs/monthly_sales.csv`

## Limitations
- Data is synthetic, not actual business data.
- Revenue does not subtract cost of goods, shipping, returns, or marketing spend.
- Segment labels are rule-based and illustrative.
- Repeat purchase rate is not the same as cohort retention.
- No causal claim should be made that the project improved business outcomes.

## Next steps
- Add profit and margin after obtaining cost data.
- Add refunds/returns and marketing campaign spend.
- Build cohort-based retention and customer lifetime value estimates.
- Add automated data validation tests and a scheduled refresh.
