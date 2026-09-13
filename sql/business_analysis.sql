-- ============================================================
-- Walmart Enterprise Demand Forecasting
-- Milestone 2.1: Advanced SQL Analytics
-- ============================================================


-- ============================================================
-- 1. Total units sold by store
-- Aggregation
-- ============================================================

SELECT
    store_id,
    SUM(units_sold) AS total_units_sold
FROM fact_sales
GROUP BY store_id
ORDER BY total_units_sold DESC;


-- ============================================================
-- 2. Total units sold by product category
-- JOIN + Aggregation
-- ============================================================

SELECT
    p.cat_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_product AS p
    ON s.item_id = p.item_id
GROUP BY p.cat_id
ORDER BY total_units_sold DESC;


-- ============================================================
-- 3. Store sales performance using a CTE
-- ============================================================

WITH store_sales AS (
    SELECT
        store_id,
        SUM(units_sold) AS total_units_sold
    FROM fact_sales
    GROUP BY store_id
)

SELECT
    store_id,
    total_units_sold
FROM store_sales
ORDER BY total_units_sold DESC;


-- ============================================================
-- 4. Rank stores by total unit sales
-- CTE + Window Function
-- ============================================================

WITH store_sales AS (
    SELECT
        store_id,
        SUM(units_sold) AS total_units_sold
    FROM fact_sales
    GROUP BY store_id
)

SELECT
    store_id,
    total_units_sold,
    RANK() OVER (
        ORDER BY total_units_sold DESC
    ) AS sales_rank
FROM store_sales
ORDER BY sales_rank;


-- ============================================================
-- 5. Daily total Walmart sales
-- Aggregation
-- ============================================================

SELECT
    date,
    SUM(units_sold) AS daily_units_sold
FROM fact_sales
GROUP BY date
ORDER BY date;


-- ============================================================
-- 6. Daily sales with previous-day comparison
-- CTE + LAG Window Function
-- ============================================================

WITH daily_sales AS (
    SELECT
        date,
        SUM(units_sold) AS daily_units_sold
    FROM fact_sales
    GROUP BY date
)

SELECT
    date,
    daily_units_sold,
    LAG(daily_units_sold) OVER (
        ORDER BY date
    ) AS previous_day_sales,
    daily_units_sold
        - LAG(daily_units_sold) OVER (
            ORDER BY date
        ) AS daily_change
FROM daily_sales
ORDER BY date;


-- ============================================================
-- 7. 7-day rolling average of Walmart sales
-- Window Function
-- ============================================================

WITH daily_sales AS (
    SELECT
        date,
        SUM(units_sold) AS daily_units_sold
    FROM fact_sales
    GROUP BY date
)

SELECT
    date,
    daily_units_sold,
    AVG(daily_units_sold) OVER (
        ORDER BY date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS rolling_7_day_avg
FROM daily_sales
ORDER BY date;


-- ============================================================
-- 8. Total units sold by state
-- JOIN + Aggregation
-- ============================================================

SELECT
    st.state_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_store AS st
    ON s.store_id = st.store_id
GROUP BY st.state_id
ORDER BY total_units_sold DESC;


-- ============================================================
-- 9. Total units sold by department
-- JOIN + Aggregation
-- ============================================================

SELECT
    p.dept_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_product AS p
    ON s.item_id = p.item_id
GROUP BY p.dept_id
ORDER BY total_units_sold DESC;


-- ============================================================
-- 10. Top 10 products by total units sold
-- JOIN + Aggregation + Ranking
-- ============================================================

WITH product_sales AS (
    SELECT
        s.item_id,
        p.cat_id,
        p.dept_id,
        SUM(s.units_sold) AS total_units_sold
    FROM fact_sales AS s
    JOIN dim_product AS p
        ON s.item_id = p.item_id
    GROUP BY
        s.item_id,
        p.cat_id,
        p.dept_id
)

SELECT
    item_id,
    cat_id,
    dept_id,
    total_units_sold,
    RANK() OVER (
        ORDER BY total_units_sold DESC
    ) AS product_rank
FROM product_sales
ORDER BY product_rank
LIMIT 10;


-- ============================================================
-- 11. Average selling price by category
-- JOIN + Aggregation
-- ============================================================

SELECT
    p.cat_id,
    ROUND(
        AVG(fp.sell_price),
        2
    ) AS average_sell_price
FROM fact_prices AS fp
JOIN dim_product AS p
    ON fp.item_id = p.item_id
GROUP BY p.cat_id
ORDER BY average_sell_price DESC;


-- ============================================================
-- 12. Product price history with previous price
-- LAG Window Function
-- ============================================================

SELECT
    store_id,
    item_id,
    wm_yr_wk,
    sell_price,
    LAG(sell_price) OVER (
        PARTITION BY
            store_id,
            item_id
        ORDER BY wm_yr_wk
    ) AS previous_price
FROM fact_prices
ORDER BY
    store_id,
    item_id,
    wm_yr_wk;


-- ============================================================
-- 13. Price change from previous Walmart week
-- Window Function
-- ============================================================

WITH price_history AS (
    SELECT
        store_id,
        item_id,
        wm_yr_wk,
        sell_price,
        LAG(sell_price) OVER (
            PARTITION BY
                store_id,
                item_id
            ORDER BY wm_yr_wk
        ) AS previous_price
    FROM fact_prices
)

SELECT
    store_id,
    item_id,
    wm_yr_wk,
    sell_price,
    previous_price,
    sell_price - previous_price AS price_change
FROM price_history
WHERE previous_price IS NOT NULL
ORDER BY
    store_id,
    item_id,
    wm_yr_wk;


-- ============================================================
-- 14. Store-category sales performance
-- Multiple JOINs + Aggregation
-- ============================================================

SELECT
    s.store_id,
    p.cat_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_product AS p
    ON s.item_id = p.item_id
GROUP BY
    s.store_id,
    p.cat_id
ORDER BY
    s.store_id,
    total_units_sold DESC;


-- ============================================================
-- 15. Monthly Walmart sales
-- JOIN to Calendar + Aggregation
-- ============================================================

SELECT
    c.year,
    c.month,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_calendar AS c
    ON s.date = c.date
GROUP BY
    c.year,
    c.month
ORDER BY
    c.year,
    c.month;


-- ============================================================
-- 16. Holiday vs non-holiday sales
-- Conditional Aggregation
-- ============================================================

SELECT
    CASE
        WHEN c.event_name_1 IS NOT NULL
            OR c.event_name_2 IS NOT NULL
        THEN 'Holiday/Event'
        ELSE 'Regular Day'
    END AS day_type,
    SUM(s.units_sold) AS total_units_sold,
    ROUND(
        AVG(s.units_sold),
        4
    ) AS average_units_per_record
FROM fact_sales AS s
JOIN dim_calendar AS c
    ON s.date = c.date
GROUP BY day_type
ORDER BY total_units_sold DESC;


-- ============================================================
-- 17. Create reusable daily sales view
-- VIEW
-- ============================================================

CREATE OR REPLACE VIEW vw_daily_sales AS

SELECT
    date,
    SUM(units_sold) AS daily_units_sold
FROM fact_sales
GROUP BY date;


-- ============================================================
-- 18. Query daily sales view
-- ============================================================

SELECT *
FROM vw_daily_sales
ORDER BY date
LIMIT 30;


-- ============================================================
-- 19. Create reusable store sales view
-- VIEW
-- ============================================================

CREATE OR REPLACE VIEW vw_store_sales_summary AS

SELECT
    store_id,
    SUM(units_sold) AS total_units_sold,
    AVG(units_sold) AS average_units_sold
FROM fact_sales
GROUP BY store_id;


-- ============================================================
-- 20. Query store sales view
-- ============================================================

SELECT *
FROM vw_store_sales_summary
ORDER BY total_units_sold DESC;

-- ============================================================
-- 21. Store performance ranking view
-- CTE + Window Function
-- ============================================================

CREATE OR REPLACE VIEW vw_store_performance AS

WITH store_sales AS (
    SELECT
        store_id,
        SUM(units_sold) AS total_units_sold
    FROM fact_sales
    GROUP BY store_id
)

SELECT
    store_id,
    total_units_sold,
    RANK() OVER (
        ORDER BY total_units_sold DESC
    ) AS sales_rank
FROM store_sales;


-- ============================================================
-- 22. Category performance view
-- JOIN + Aggregation
-- ============================================================

CREATE OR REPLACE VIEW vw_category_performance AS

SELECT
    p.cat_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_product AS p
    ON s.item_id = p.item_id
GROUP BY p.cat_id;


-- ============================================================
-- 23. Monthly sales view
-- Time-based Aggregation
-- ============================================================

CREATE OR REPLACE VIEW vw_monthly_sales AS

SELECT
    EXTRACT(YEAR FROM date)::INT AS year,
    EXTRACT(MONTH FROM date)::INT AS month,
    SUM(units_sold) AS total_units_sold
FROM fact_sales
GROUP BY
    EXTRACT(YEAR FROM date),
    EXTRACT(MONTH FROM date);


-- ============================================================
-- 24. State performance view
-- JOIN + Aggregation
-- ============================================================

CREATE OR REPLACE VIEW vw_state_performance AS

SELECT
    st.state_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_store AS st
    ON s.store_id = st.store_id
GROUP BY st.state_id;


-- ============================================================
-- 25. Product performance view
-- JOIN + Aggregation
-- ============================================================

CREATE OR REPLACE VIEW vw_product_performance AS

SELECT
    s.item_id,
    p.dept_id,
    p.cat_id,
    SUM(s.units_sold) AS total_units_sold
FROM fact_sales AS s
JOIN dim_product AS p
    ON s.item_id = p.item_id
GROUP BY
    s.item_id,
    p.dept_id,
    p.cat_id;


-- ============================================================
-- 26. Sales with price view
-- Sales + Calendar + Price Join
-- ============================================================

CREATE OR REPLACE VIEW vw_sales_with_price AS

SELECT
    s.store_id,
    s.item_id,
    s.date,
    s.units_sold,
    p.sell_price
FROM fact_sales AS s
JOIN dim_calendar AS c
    ON s.date = c.date
JOIN fact_prices AS p
    ON s.store_id = p.store_id
    AND s.item_id = p.item_id
    AND c.wm_yr_wk = p.wm_yr_wk;


-- ============================================================
-- 27. Sales revenue view
-- Revenue = Units Sold × Sell Price
-- ============================================================

CREATE OR REPLACE VIEW vw_sales_revenue AS

SELECT
    store_id,
    item_id,
    date,
    units_sold,
    sell_price,
    units_sold * sell_price AS revenue
FROM vw_sales_with_price;


-- ============================================================
-- 28. Store revenue view
-- ============================================================

CREATE OR REPLACE VIEW vw_store_revenue AS

SELECT
    store_id,
    ROUND(
        SUM(revenue),
        2
    ) AS total_revenue
FROM vw_sales_revenue
GROUP BY store_id;


-- ============================================================
-- 29. Category revenue view
-- ============================================================

CREATE OR REPLACE VIEW vw_category_revenue AS

SELECT
    p.cat_id,
    ROUND(
        SUM(r.revenue),
        2
    ) AS total_revenue
FROM vw_sales_revenue AS r
JOIN dim_product AS p
    ON r.item_id = p.item_id
GROUP BY p.cat_id;


-- ============================================================
-- 30. Weekly product price changes
-- LAG + PARTITION BY
-- ============================================================

WITH price_changes AS (
    SELECT
        store_id,
        item_id,
        wm_yr_wk,
        sell_price,
        LAG(sell_price) OVER (
            PARTITION BY store_id, item_id
            ORDER BY wm_yr_wk
        ) AS previous_price
    FROM fact_prices
)

SELECT
    store_id,
    item_id,
    wm_yr_wk,
    previous_price,
    sell_price,
    ROUND(
        sell_price - previous_price,
        2
    ) AS price_change
FROM price_changes
WHERE previous_price IS NOT NULL
  AND sell_price <> previous_price
ORDER BY
    store_id,
    item_id,
    wm_yr_wk
LIMIT 30;


-- ============================================================
-- 31. Performance indexes
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_sales_date
ON fact_sales(date);

CREATE INDEX IF NOT EXISTS idx_fact_sales_store
ON fact_sales(store_id);

CREATE INDEX IF NOT EXISTS idx_fact_sales_item
ON fact_sales(item_id);

CREATE INDEX IF NOT EXISTS idx_fact_prices_lookup
ON fact_prices(
    store_id,
    item_id,
    wm_yr_wk
);