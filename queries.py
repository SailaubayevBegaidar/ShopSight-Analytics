import pandas as pd
import psycopg2
import plotly.graph_objects as go
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

# Загрузка переменных окружения
load_dotenv()

# Конфигурация подключения
class Settings(BaseSettings):
    DB_NAME: str = os.getenv("DB_NAME", "olist")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# SQL-запрос: Тренд продаж по месяцам
query = """
SELECT 
    DATE_TRUNC('month', o.order_purchase_timestamp) AS month,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(op.payment_value)::numeric, 2) AS total_revenue
FROM olist_orders o
JOIN olist_order_payments op ON o.order_id = op.order_id
GROUP BY month
ORDER BY month;
"""

# Получение данных
conn = psycopg2.connect(settings.DATABASE_URL)
df = pd.read_sql(query, conn)
conn.close()

# Подготовка данных
df['month'] = pd.to_datetime(df['month'])

# Построение графика с range slider
fig = go.Figure()

# Линия для заказов
fig.add_trace(go.Scatter(
    x=df['month'],
    y=df['total_orders'],
    mode='lines+markers',
    name='Заказы'
))

# Линия для выручки
fig.add_trace(go.Scatter(
    x=df['month'],
    y=df['total_revenue'],
    mode='lines+markers',
    name='Выручка (BRL)',
    yaxis="y2"
))

# Настройка layout
fig.update_layout(
    title="Эволюция продаж по месяцам",
    xaxis=dict(
        rangeselector=dict(
            buttons=list([
                dict(count=3, label="3m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(visible=True),
        type="date"
    ),
    yaxis=dict(
        title="Количество заказов"
    ),
    yaxis2=dict(
        title="Выручка (BRL)",
        overlaying="y",
        side="right"
    ),
    legend=dict(x=0.01, y=0.99),
    plot_bgcolor="rgba(245,245,245,1)"
)

fig.show()
