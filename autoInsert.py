import time
import random
import string
import psycopg2
from datetime import datetime
from config import settings

conn = psycopg2.connect(settings.DATABASE_URL)
cursor = conn.cursor()

categories = [ "moveis_decoracao", "papelaria"]

def random_product_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=32))

while True:
    product_id = random_product_id()
    category = random.choice(categories)
    name_length = random.randint(35, 60)
    desc_length = random.randint(200, 400)
    photos_qty = random.randint(1, 5)
    weight_g = random.randint(100, 2000)
    length_cm = random.randint(10, 50)
    height_cm = random.randint(5, 25)
    width_cm = random.randint(10, 30)

    cursor.execute("""
        INSERT INTO olist_products (
            product_id,
            product_category_name,
            product_name_lenght,
            product_description_lenght,
            product_photos_qty,
            product_weight_g,
            product_length_cm,
            product_height_cm,
            product_width_cm
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        product_id, category, name_length, desc_length, photos_qty,
        weight_g, length_cm, height_cm, width_cm
    ))

    conn.commit()

    print(f" Inserted product {product_id[:6]}... ({category}) " f"{weight_g}g {length_cm}x{width_cm}x{height_cm}cm")
    
    time.sleep(10)