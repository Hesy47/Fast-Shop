from fastapi import FastAPI, Depends, Query, status
from fastapi.responses import JSONResponse
from dependencies import get_db_fast
from sqlalchemy.orm import Session
from models import Collection
from schema import GetAllCollectionsSchema, CreateCollectionSchema
from schema import UpdateCollectionSchema, DeleteCollectionSchema, GetCollection
import uvicorn

app = FastAPI(debug=True)


@app.get("/get-collection/{collection_id}", response_model=GetCollection)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db_fast),
):

    collection_query = (
        db.query(Collection).filter(Collection.id == collection_id).first()
    )

    if collection_query is None:
        return JSONResponse(
            {"message": "we do not have such this collection"},
            status.HTTP_404_NOT_FOUND,
        )

    return {"item": collection_query, "status": "200"}


@app.get("/get-all-collections", response_model=GetAllCollectionsSchema)
async def get_all_collections(
    page: int = Query(1, ge=1),
    per_page: int = Query(16, le=20),
    db: Session = Depends(get_db_fast),
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


@app.post("/create-collection")
async def create_collection(
    input_collection: CreateCollectionSchema,
    db: Session = Depends(get_db_fast),
):

    new_collection = Collection(**input_collection.model_dump())

    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    return {
        "response": "new collection by the name of "
        f"{new_collection.title} has been created successfully"
    }


@app.patch("/update-collection/{collection_id}")
async def update_collection(
    collection_id: int,
    input_collection: UpdateCollectionSchema,
    db: Session = Depends(get_db_fast),
):
    collection_query = (
        db.query(Collection).filter(Collection.id == collection_id).first()
    )

    if collection_query is None:
        return JSONResponse(
            {"message": "we do not have such this collection"},
            status.HTTP_404_NOT_FOUND,
        )

    collection_query.title = input_collection.model_dump().get("title")
    db.commit()

    return JSONResponse(
        {"message": "the collection updated successfully"},
        status.HTTP_202_ACCEPTED,
    )


@app.delete("/delete-collection")
async def delete_collection(
    input_collection: DeleteCollectionSchema,
    db: Session = Depends(get_db_fast),
):
    collection_query = (
        db.query(Collection)
        .filter(Collection.title == input_collection.model_dump().get("title"))
        .first()
    )

    if collection_query is None:
        return JSONResponse(
            {"message": "we do not have such this collection"},
            status.HTTP_404_NOT_FOUND,
        )

    db.delete(collection_query)
    db.commit()

    return JSONResponse(
        {
            "message": "the collection with name of "
            f"{collection_query.title} has been deleted successfully"
        },
        status.HTTP_202_ACCEPTED,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
