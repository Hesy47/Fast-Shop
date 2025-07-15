from models import Collection
from dependencies import get_db_python

with get_db_python() as db:
    query1 = (
        db.query(Collection)
        .filter(Collection.title == "collection44" or Collection.title == "collection4")
        .first()
    )
    print(query1.title)
