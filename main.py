import psycopg2
from config import settings
from tabulate import tabulate

class DatabaseAnalytics:
    def __init__(self):
        self.db_params = {
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT
        }

    def execute_query(self, query: str, description: str) -> None:
        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    print(f"\n=== {description} ===")
                    cur.execute(query)
                    rows = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Exception as e:
            print(f"Error executing query: {e}")

    def run_analytics(self):
        # Query 1: Top selling products
        top_products_query = """
        SELECT p.product_category_name, COUNT(*) as total_sales
        FROM olist_order_items oi
        JOIN olist_products p ON oi.product_id = p.product_id
        GROUP BY p.product_category_name
        ORDER BY total_sales DESC
        LIMIT 10
        """
        
        # Query 2: Average order value by state
        avg_order_query = """
        SELECT 
            c.customer_state, 
            ROUND(AVG(op.payment_value)::numeric, 2) as avg_order_value
        FROM olist_orders o
        JOIN olist_customers c ON o.customer_id = c.customer_id
        JOIN olist_order_payments op ON o.order_id = op.order_id
        GROUP BY c.customer_state
        ORDER BY avg_order_value DESC
        """
        
        # Query 3: Customer satisfaction by seller
        satisfaction_query = """
        SELECT 
            s.seller_id, 
            ROUND(AVG(r.review_score)::numeric, 2) as avg_score,
            COUNT(r.review_id) as total_reviews
        FROM olist_order_reviews r
        JOIN olist_order_items oi ON r.order_id = oi.order_id
        JOIN olist_sellers s ON oi.seller_id = s.seller_id
        GROUP BY s.seller_id
        HAVING COUNT(r.review_id) > 10
        ORDER BY avg_score DESC
        LIMIT 10
        """
        
        # Execute all queries
        self.execute_query(top_products_query, "Top Selling Product Categories")
        self.execute_query(avg_order_query, "Average Order Value by State")
        self.execute_query(satisfaction_query, "Top 10 Sellers by Customer Satisfaction")

def main():
    analytics = DatabaseAnalytics()
    analytics.run_analytics()

if __name__ == "__main__":
    main()