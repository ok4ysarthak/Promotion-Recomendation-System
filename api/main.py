import sre_compile
from fastapi import FastAPI
import psycopg2
import psycopg2.extras
from typing import List
from pydantic import BaseModel
import datetime

app = FastAPI(title="Retail Promotions Dashboard API")

class Promotion(BaseModel):
    id:int
    customer_id:str
    product_id:str
    discount: str
    created_at: datetime.datetime

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="retail",
        user="postgres",
        password="password"
    )

@app.get("/promotions", response_model=List[Promotion])

def read_promotions():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute("SELECT * FROM promotions ORDER BY created_at DESC;")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        result.append(Promotion(
            id=row['id'],
            customer_id=row['customer_id'],
            product_id=row['product_id'],
            discount=row['discount'],
            created_at=row['created_at']
        ))
    cursor.close()
    conn.close()
    return result