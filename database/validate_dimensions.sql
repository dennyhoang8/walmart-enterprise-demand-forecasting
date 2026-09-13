-- ==========================================
-- Validate Dimension Tables
-- ==========================================

SELECT COUNT(*) AS total_products
FROM dim_product;

SELECT COUNT(*) AS total_stores
FROM dim_store;

SELECT COUNT(*) AS total_calendar_days
FROM dim_calendar;


SELECT *
FROM dim_product
LIMIT 5;


SELECT *
FROM dim_store;


SELECT *
FROM dim_calendar
LIMIT 5;