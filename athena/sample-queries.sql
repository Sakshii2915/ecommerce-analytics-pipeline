-- Sample Athena Queries for E-Commerce Analytics
-- Database: ecommerce_analytics_db
-- Table: transactions

-- ============================================
-- REVENUE ANALYTICS
-- ============================================

-- 1. Total Revenue by Date
SELECT 
    DATE(transaction_date) as transaction_day,
    SUM(total_amount) as daily_revenue,
    COUNT(*) as transaction_count,
    AVG(total_amount) as avg_transaction_value
FROM transactions
WHERE year = 2024  -- Partition pruning for performance
GROUP BY DATE(transaction_date)
ORDER BY transaction_day DESC
LIMIT 30;

-- 2. Revenue Trends by Month
SELECT 
    year,
    month,
    SUM(total_amount) as monthly_revenue,
    COUNT(*) as transaction_count,
    AVG(total_amount) as avg_transaction_value,
    SUM(quantity) as total_items_sold
FROM transactions
GROUP BY year, month
ORDER BY year DESC, month DESC;

-- 3. Revenue by Quarter
SELECT 
    year,
    quarter,
    SUM(total_amount) as quarterly_revenue,
    COUNT(*) as transaction_count,
    SUM(quantity) as total_items_sold
FROM transactions
GROUP BY year, quarter
ORDER BY year DESC, quarter DESC;

-- ============================================
-- PRODUCT & CATEGORY ANALYTICS
-- ============================================

-- 4. Top 10 Best-Selling Products by Revenue
SELECT 
    product_id,
    product_name,
    category,
    SUM(total_amount) as total_revenue,
    SUM(quantity) as total_quantity_sold,
    COUNT(*) as transaction_count,
    AVG(price) as avg_price
FROM transactions
GROUP BY product_id, product_name, category
ORDER BY total_revenue DESC
LIMIT 10;

-- 5. Top Categories by Revenue
SELECT 
    category,
    SUM(total_amount) as category_revenue,
    COUNT(*) as transaction_count,
    SUM(quantity) as total_items_sold,
    AVG(total_amount) as avg_transaction_value
FROM transactions
GROUP BY category
ORDER BY category_revenue DESC;

-- 6. Product Performance Analysis
SELECT 
    product_id,
    product_name,
    category,
    COUNT(DISTINCT customer_id) as unique_customers,
    SUM(quantity) as total_quantity_sold,
    SUM(total_amount) as total_revenue,
    AVG(quantity) as avg_quantity_per_transaction
FROM transactions
GROUP BY product_id, product_name, category
HAVING total_revenue > 10000  -- Filter for significant products
ORDER BY total_revenue DESC;

-- ============================================
-- TIME-BASED ANALYTICS
-- ============================================

-- 7. Peak Transaction Hours
SELECT 
    hour,
    COUNT(*) as transaction_count,
    SUM(total_amount) as hourly_revenue,
    AVG(total_amount) as avg_transaction_value
FROM transactions
GROUP BY hour
ORDER BY transaction_count DESC;

-- 8. Day of Week Analysis
SELECT 
    CASE day_of_week
        WHEN 1 THEN 'Sunday'
        WHEN 2 THEN 'Monday'
        WHEN 3 THEN 'Tuesday'
        WHEN 4 THEN 'Wednesday'
        WHEN 5 THEN 'Thursday'
        WHEN 6 THEN 'Friday'
        WHEN 7 THEN 'Saturday'
    END as day_name,
    COUNT(*) as transaction_count,
    SUM(total_amount) as daily_revenue,
    AVG(total_amount) as avg_transaction_value
FROM transactions
GROUP BY day_of_week
ORDER BY day_of_week;

-- 9. Hourly Revenue Pattern
SELECT 
    hour,
    COUNT(*) as transaction_count,
    SUM(total_amount) as hourly_revenue
FROM transactions
WHERE year = 2024 AND month >= 10  -- Recent data
GROUP BY hour
ORDER BY hour;

-- ============================================
-- CUSTOMER ANALYTICS
-- ============================================

-- 10. Top Customers by Revenue
SELECT 
    customer_id,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_spent,
    AVG(total_amount) as avg_transaction_value,
    MIN(transaction_date) as first_purchase_date,
    MAX(transaction_date) as last_purchase_date
FROM transactions
GROUP BY customer_id
HAVING transaction_count >= 5  -- Customers with 5+ transactions
ORDER BY total_spent DESC
LIMIT 50;

-- 11. Customer Lifetime Value (CLV) Analysis
SELECT 
    customer_id,
    COUNT(*) as total_transactions,
    SUM(total_amount) as lifetime_value,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT DATE(transaction_date)) as active_days,
    DATEDIFF('day', MIN(transaction_date), MAX(transaction_date)) as customer_lifespan_days
FROM transactions
GROUP BY customer_id
ORDER BY lifetime_value DESC;

-- ============================================
-- PAYMENT & REGIONAL ANALYTICS
-- ============================================

-- 12. Payment Method Analysis
SELECT 
    payment_method,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value,
    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM transactions) as percentage
FROM transactions
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- 13. Revenue by Region
SELECT 
    region,
    COUNT(*) as transaction_count,
    SUM(total_amount) as regional_revenue,
    AVG(total_amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
GROUP BY region
ORDER BY regional_revenue DESC;

-- 14. Store Performance
SELECT 
    store_id,
    region,
    COUNT(*) as transaction_count,
    SUM(total_amount) as store_revenue,
    AVG(total_amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
GROUP BY store_id, region
ORDER BY store_revenue DESC
LIMIT 20;

-- ============================================
-- ADVANCED ANALYTICS & KPIs
-- ============================================

-- 15. Overall Business KPIs
SELECT 
    COUNT(*) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    COUNT(DISTINCT product_id) as unique_products,
    SUM(total_amount) as total_revenue,
    SUM(quantity) as total_items_sold,
    AVG(total_amount) as avg_transaction_value,
    MIN(transaction_date) as first_transaction,
    MAX(transaction_date) as last_transaction
FROM transactions;

-- 16. Monthly Growth Rate (Revenue)
WITH monthly_revenue AS (
    SELECT 
        year,
        month,
        SUM(total_amount) as revenue
    FROM transactions
    GROUP BY year, month
),
monthly_growth AS (
    SELECT 
        year,
        month,
        revenue,
        LAG(revenue) OVER (ORDER BY year, month) as prev_month_revenue
    FROM monthly_revenue
)
SELECT 
    year,
    month,
    revenue,
    prev_month_revenue,
    CASE 
        WHEN prev_month_revenue > 0 
        THEN ((revenue - prev_month_revenue) / prev_month_revenue * 100)
        ELSE NULL 
    END as growth_percentage
FROM monthly_growth
ORDER BY year DESC, month DESC;

-- 17. Product Category Performance Over Time
SELECT 
    category,
    year,
    month,
    SUM(total_amount) as monthly_revenue,
    COUNT(*) as transaction_count
FROM transactions
WHERE year = 2024
GROUP BY category, year, month
ORDER BY category, year DESC, month DESC;

-- 18. Basket Size Analysis
SELECT 
    quantity,
    COUNT(*) as transaction_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_transaction_value
FROM transactions
GROUP BY quantity
ORDER BY quantity;

-- 19. High-Value Transactions
SELECT 
    transaction_id,
    customer_id,
    product_name,
    category,
    total_amount,
    transaction_date,
    payment_method
FROM transactions
WHERE total_amount > 200  -- High-value threshold
ORDER BY total_amount DESC
LIMIT 100;

-- 20. Category Revenue Share
SELECT 
    category,
    SUM(total_amount) as category_revenue,
    SUM(total_amount) * 100.0 / (SELECT SUM(total_amount) FROM transactions) as revenue_percentage
FROM transactions
GROUP BY category
ORDER BY category_revenue DESC;

