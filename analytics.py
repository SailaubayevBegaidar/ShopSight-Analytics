import psycopg2
from config import settings
from tabulate import tabulate
import matplotlib.pyplot as plt
import os


class DatabaseAnalytics:
    def __init__(self):
        self.db_params = {
            "dbname": settings.DB_NAME,
            "user": settings.DB_USER,
            "password": settings.DB_PASSWORD,
            "host": settings.DB_HOST,
            "port": settings.DB_PORT
        }
        self.charts_dir = "charts"
        os.makedirs(self.charts_dir, exist_ok=True)

    def execute_query(self, query: str, description: str, chart_type: str = None) -> None:
        try:
            with psycopg2.connect(**self.db_params) as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]

                    print(f"\n=== {description} ===")
                    print(tabulate(rows, headers=headers, tablefmt="grid"))
                    print(f"Rows fetched: {len(rows)}")

                    # Если указан тип графика → рисуем
                    if chart_type and rows:
                        self.create_chart(rows, headers, description, chart_type)

        except Exception as e:
            print(f"Error executing query [{description}]: {e}")

    def create_chart(self, rows, headers, description, chart_type):
        filename = os.path.join(self.charts_dir, f"{description.replace(' ', '_')}.png")

        if chart_type == "pie":
            labels = [row[0] for row in rows]
            sizes = [row[1] for row in rows]

            plt.figure(figsize=(8, 8))
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
            plt.title(description)
            plt.legend(labels, title=headers[0])

        elif chart_type == "bar":
            labels = [row[0] for row in rows]
            values = [row[1] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.bar(labels, values)
            plt.xlabel(headers[0])
            plt.ylabel(headers[1])
            plt.title(description)
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "barh":
            labels = [row[0] for row in rows]
            values = [row[1] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.barh(labels, values)
            plt.xlabel(headers[1])
            plt.ylabel(headers[0])
            plt.title(description)

        elif chart_type == "line":
            x = [row[0] for row in rows]
            y = [row[1] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.plot(x, y, marker="o", label=headers[1])
            plt.xlabel(headers[0])
            plt.ylabel(headers[1])
            plt.title(description)
            plt.xticks(rotation=45, ha="right")
            plt.legend()

        elif chart_type == "hist":
            values = [row[0] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.hist(values, bins=10, edgecolor="black")
            plt.xlabel(headers[0])
            plt.ylabel("Frequency")
            plt.title(description)

        elif chart_type == "scatter":
            # Используем данные из запроса: total_orders (X) и avg_score (Y)
            x = [row[0] for row in rows]
            y = [row[1] for row in rows]

            plt.figure(figsize=(10, 6))
            plt.scatter(x, y, alpha=0.7)

            plt.xlabel(headers[0])  # total_orders
            plt.ylabel(headers[1])  # avg_score
            plt.title(description)
            plt.grid(True, linestyle="--", alpha=0.6)

        else:
            print(f"Chart type '{chart_type}' is not supported.")
            return

        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

        print(f"Chart saved: {filename} ({chart_type} showing {description})")

    def run_analytics(self):
        queries = [
    {
        "query": """
            SELECT 
                op.payment_type,
                COUNT(*) as usage_count
            FROM olist_order_payments op
            JOIN olist_orders o ON op.order_id = o.order_id
            JOIN olist_customers c ON o.customer_id = c.customer_id
            GROUP BY op.payment_type
            ORDER BY usage_count DESC;
        """,
        "description": "Payment Method Distribution",
        "chart_type": "pie",
        "insight": "Shows which payment methods are most popular among customers (based on orders with linked customers)."
    },
    {
        "query": """
            SELECT 
                p.product_category_name,
                COUNT(*) as total_sales
            FROM olist_order_items oi
            JOIN olist_products p ON oi.product_id = p.product_id
            JOIN olist_orders o ON oi.order_id = o.order_id
            GROUP BY p.product_category_name
            ORDER BY total_sales DESC
            LIMIT 10;
        """,
        "description": "Top Selling Product Categories",
        "chart_type": "bar",
        "insight": "Shows which product categories generate the highest sales volume across orders."
    },
    {
        "query": """
            SELECT 
                c.customer_state,
                ROUND(AVG(op.payment_value)::numeric, 2) as avg_order_value
            FROM olist_orders o
            JOIN olist_customers c ON o.customer_id = c.customer_id
            JOIN olist_order_payments op ON o.order_id = op.order_id
            JOIN olist_order_items oi ON o.order_id = oi.order_id
            GROUP BY c.customer_state
            ORDER BY avg_order_value DESC
            LIMIT 10;
        """,
        "description": "Average Order Value by State",
        "chart_type": "barh",
        "insight": "Compares customer states by average order value, including data from payments and items."
    },
    {
        "query": """
            SELECT 
                DATE_TRUNC('month', o.order_purchase_timestamp) as month,
                ROUND(SUM(op.payment_value)::numeric, 2) as total_revenue
            FROM olist_orders o
            JOIN olist_order_payments op ON o.order_id = op.order_id
            JOIN olist_customers c ON o.customer_id = c.customer_id
            GROUP BY month
            ORDER BY month;
        """,
        "description": "Monthly Sales Trend",
        "chart_type": "line",
        "insight": "Shows how revenue changes month by month across all customers."
    },
    {
        "query": """
            SELECT 
                subq.purchases
            FROM (
                SELECT 
                    c.customer_id,
                    COUNT(o.order_id) as purchases
                FROM olist_customers c
                JOIN olist_orders o ON c.customer_id = o.customer_id
                JOIN olist_order_items oi ON o.order_id = oi.order_id
                GROUP BY c.customer_id
            ) subq
            ORDER BY subq.purchases;
        """,
        "description": "Customer Purchase Frequency",
        "chart_type": "hist",
        "insight": "Shows how frequently customers make repeat purchases (based on orders and items)."
    },
    {
        "query": """
            SELECT 
                COUNT(DISTINCT oi.order_id) as total_orders,
                ROUND(AVG(r.review_score)::numeric, 2) as avg_score
            FROM olist_sellers s
            JOIN olist_order_items oi ON s.seller_id = oi.seller_id
            JOIN olist_orders o ON oi.order_id = o.order_id
            LEFT JOIN olist_order_reviews r ON o.order_id = r.order_id
            GROUP BY s.seller_id
            HAVING COUNT(r.review_id) > 10
            ORDER BY total_orders DESC
            LIMIT 50;
        """,
        "description": "Top Sellers by Satisfaction and Volume",
        "chart_type": "scatter",
        "insight": "Each point represents a seller: number of orders vs average review score (using LEFT JOIN for reviews)."
    }
]


        for q in queries:
            print(f"\n>>> Running analysis: {q['description']}")
            self.execute_query(q["query"], q["description"], chart_type=q["chart_type"])
            print(f"Insight: {q['insight']}")


def main():
    analytics = DatabaseAnalytics()
    analytics.run_analytics()


if __name__ == "__main__":
    main()
