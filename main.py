from fastapi import FastAPI, Depends, Query
from dependencies import get_db
from sqlalchemy.orm import Session
from models import Collection
from schema import GetAllCollections, CreateCollection
import uvicorn

app = FastAPI(debug=True)


@app.get("/get-all-collections", response_model=GetAllCollections)
async def get_all_collections(
    page: int = Query(1, ge=1),
    per_page: int = Query(16, le=100),
    db: Session = Depends(get_db),
):
    total_items = db.query(Collection).count()
    skip = (page - 1) * per_page

    collections_query = db.query(Collection).offset(skip).limit(per_page).all()

    has_next = (skip + per_page) < total_items
    has_previous = page > 1

    return {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "has_next": has_next,
        "has_previous": has_previous,
        "items": collections_query,
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


@app.post("/create-collection")
async def create_collection(
    collection: CreateCollection,
    db: Session = Depends(get_db),
):
    new_collection = Collection(collection)

    db.add(new_collection)
    db.commit()
    db.refresh()

    return {
        "response": "new collection by the name of "
        f"{new_collection.title} has been created successfully"
    }
