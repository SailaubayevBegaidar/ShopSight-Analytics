-- 1. Top selling product categories with their total revenue
SELECT 
    p.product_category_name,
    COUNT(*) as total_sales,
    ROUND(SUM(oi.price)::numeric, 2) as total_revenue
FROM olist_order_items oi
JOIN olist_products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC
LIMIT 10;

-- 2. Average order value by state with order count
SELECT 
    c.customer_state,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(AVG(op.payment_value)::numeric, 2) as avg_order_value
FROM olist_orders o
JOIN olist_customers c ON o.customer_id = c.customer_id
JOIN olist_order_payments op ON o.order_id = op.order_id
GROUP BY c.customer_state
ORDER BY avg_order_value DESC;

-- 3. Top sellers by customer satisfaction and sales volume
SELECT 
    s.seller_id,
    COUNT(DISTINCT oi.order_id) as total_orders,
    ROUND(AVG(r.review_score)::numeric, 2) as avg_score,
    COUNT(r.review_id) as total_reviews
FROM olist_sellers s
JOIN olist_order_items oi ON s.seller_id = oi.seller_id
LEFT JOIN olist_order_reviews r ON oi.order_id = r.order_id
GROUP BY s.seller_id
HAVING COUNT(r.review_id) > 10
ORDER BY avg_score DESC, total_orders DESC
LIMIT 10;

-- 4. Monthly sales trend
SELECT 
    DATE_TRUNC('month', o.order_purchase_timestamp) as month,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(SUM(op.payment_value)::numeric, 2) as total_revenue
FROM olist_orders o
JOIN olist_order_payments op ON o.order_id = op.order_id
GROUP BY month
ORDER BY month;

-- 5. Payment method distribution
SELECT 
    payment_type,
    COUNT(*) as usage_count,
    ROUND(AVG(payment_value)::numeric, 2) as avg_payment,
    ROUND(SUM(payment_value)::numeric, 2) as total_value
FROM olist_order_payments
GROUP BY payment_type
ORDER BY usage_count DESC;

-- 6. Delivery performance analysis
SELECT 
    DATE_TRUNC('month', order_purchase_timestamp) as month,
    COUNT(*) as total_deliveries,
    ROUND(AVG(EXTRACT(EPOCH FROM (order_delivered_customer_date - order_purchase_timestamp))/86400)::numeric, 2) as avg_delivery_days,
    COUNT(CASE WHEN order_delivered_customer_date > order_estimated_delivery_date THEN 1 END) as late_deliveries
FROM olist_orders
WHERE order_status = 'delivered'
GROUP BY month
ORDER BY month;

-- 7. Customer purchase frequency
SELECT 
    purchases,
    COUNT(*) as customer_count
FROM (
    SELECT 
        customer_id,
        COUNT(*) as purchases
    FROM olist_orders
    GROUP BY customer_id
) subq
GROUP BY purchases
ORDER BY purchases;

-- 8. Product categories by average review score
SELECT 
    p.product_category_name,
    COUNT(r.review_id) as total_reviews,
    ROUND(AVG(r.review_score)::numeric, 2) as avg_score
FROM olist_products p
JOIN olist_order_items oi ON p.product_id = oi.product_id
JOIN olist_order_reviews r ON oi.order_id = r.order_id
GROUP BY p.product_category_name
HAVING COUNT(r.review_id) > 10
ORDER BY avg_score DESC;

-- 9. Seller geographic distribution and performance
SELECT 
    s.seller_state,
    COUNT(DISTINCT s.seller_id) as seller_count,
    ROUND(AVG(r.review_score)::numeric, 2) as avg_review_score,
    COUNT(DISTINCT o.order_id) as total_orders
FROM olist_sellers s
JOIN olist_order_items oi ON s.seller_id = oi.seller_id
JOIN olist_orders o ON oi.order_id = o.order_id
LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
GROUP BY s.seller_state
ORDER BY seller_count DESC;

-- 10. Price range analysis by category
SELECT 
    p.product_category_name,
    COUNT(*) as product_count,
    ROUND(MIN(oi.price)::numeric, 2) as min_price,
    ROUND(AVG(oi.price)::numeric, 2) as avg_price,
    ROUND(MAX(oi.price)::numeric, 2) as max_price
FROM olist_products p
JOIN olist_order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_category_name
ORDER BY product_count DESC;