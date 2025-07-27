from dependencies import get_db_python
from models import Collection, Product
from sqlalchemy.orm import joinedload
from time import time

with get_db_python() as db:
    time_1 = time()
    query_1 = db.query(Collection).options(joinedload(Product.collection)).all()
    query_main = query_1[0].products
    print(list(query_main))
    time_2 = time()

print(f"final time: {time_2-time_1}")
