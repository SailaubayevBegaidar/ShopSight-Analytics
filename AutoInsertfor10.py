import time
import random
import string
import psycopg2
from datetime import datetime, timedelta
from config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cursor = conn.cursor()

while True:
    # Получаем случайный order_id
    cursor.execute("SELECT order_id FROM olist_orders ORDER BY RANDOM() LIMIT 1;")
    result = cursor.fetchone()

    if not result:
        print("⚠️ Нет заказов в таблице olist_orders!")
        break

    order_id = result[0]

    # Проверяем последний payment_sequential для этого order_id
    cursor.execute("""
        SELECT COALESCE(MAX(payment_sequential), 0)
        FROM olist_order_payments
        WHERE order_id = %s;
    """, (order_id,))
    last_seq = cursor.fetchone()[0]
    next_seq = last_seq + 1

    payment_value = round(random.uniform(50, 5000), 2)
    payment_type = random.choice(["credit_card", "boleto", "debit_card", "voucher"])
    payment_installments = random.randint(1, 12)

    cursor.execute("""
        INSERT INTO olist_order_payments (order_id, payment_sequential, payment_type, payment_installments, payment_value)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        order_id, next_seq, payment_type, payment_installments, payment_value
    ))

    conn.commit()

    print(f"✅ Added payment seq {next_seq} for order {order_id[:6]}... | {payment_value} ({payment_type})")
    time.sleep(10)
