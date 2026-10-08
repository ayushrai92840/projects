-- E-Commerce Customer Analytics (SQLite-compatible)
-- Run after src/generate_data.py and src/analyze.py, using outputs/ecommerce_analytics.db.

-- 1. Executive KPIs
SELECT
  ROUND(SUM(quantity * unit_price * (1 - discount_pct)), 2) AS total_revenue,
  COUNT(DISTINCT order_id) AS total_orders,
  COUNT(DISTINCT customer_id) AS active_customers,
  SUM(quantity) AS units_sold,
  ROUND(SUM(quantity * unit_price * (1 - discount_pct)) * 1.0 /
        COUNT(DISTINCT order_id), 2) AS average_order_value
FROM transactions;

-- 2. Monthly revenue trend
SELECT strftime('%Y-%m', order_date) AS order_month,
       ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders
FROM transactions
GROUP BY strftime('%Y-%m', order_date)
ORDER BY order_month;

-- 3. Category performance
SELECT category, ROUND(SUM(revenue), 2) AS revenue,
       SUM(quantity) AS units_sold,
       COUNT(DISTINCT order_id) AS orders
FROM transactions
GROUP BY category
ORDER BY revenue DESC;

-- 4. Top products by revenue
SELECT product_name, category, ROUND(SUM(revenue), 2) AS revenue,
       SUM(quantity) AS units_sold
FROM transactions
GROUP BY product_id, product_name, category
ORDER BY revenue DESC
LIMIT 15;

-- 5. Repeat purchase behaviour
WITH customer_orders AS (
  SELECT customer_id, COUNT(DISTINCT order_id) AS order_count,
         SUM(revenue) AS customer_revenue
  FROM transactions
  GROUP BY customer_id
)
SELECT
  COUNT(*) AS customers,
  SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_customers,
  ROUND(100.0 * SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) / COUNT(*), 2)
    AS repeat_customer_rate_pct,
  ROUND(AVG(order_count), 2) AS avg_orders_per_customer
FROM customer_orders;

-- 6. Regional performance
SELECT region, ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT customer_id) AS customers
FROM transactions
GROUP BY region
ORDER BY revenue DESC;

-- 7. Channel performance
SELECT channel, ROUND(SUM(revenue), 2) AS revenue,
       COUNT(DISTINCT order_id) AS orders,
       ROUND(AVG(revenue), 2) AS average_line_revenue
FROM transactions
GROUP BY channel
ORDER BY revenue DESC;
