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
        with open('sql/queries.sql', 'r') as file:
            content = file.read().strip()

        # Split queries by semicolon, but keep comments above each query
        blocks = content.split(';')

        for block in blocks:
            block = block.strip()
            if not block:
                continue

            lines = block.splitlines()
            # If first line starts with `--`, use it as description
            if lines[0].startswith('--'):
                description = lines[0].replace('--', '').strip()
                query = "\n".join(lines[1:]).strip()
            else:
                description = "SQL Query"
                query = "\n".join(lines).strip()

            if query:  # only run if there's actual SQL
                self.execute_query(query, description)


def main():
    analytics = DatabaseAnalytics()
    analytics.run_analytics()

if __name__ == "__main__":
    main()
