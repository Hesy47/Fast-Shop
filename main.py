from fastapi import FastAPI, Depends, Query, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from dependencies import get_db_fast
from sqlalchemy.orm import Session, joinedload
from models import Collection, Product
from schema import GetAllCollectionsSchema, CreateCollectionSchema
from schema import UpdateCollectionSchema, DeleteCollectionSchema, GetCollectionSchema
from schema import GetProductSchema, GetAllProductsSchema, CreateProductSchema
import uvicorn
import shutil
import os

app = FastAPI(debug=True)

if not os.path.isdir("static"):
    os.mkdir("static")
    print("static folder created...")

if not os.path.isdir("static/images"):
    os.mkdir("static/images")
    print("images folder created...")

app.mount("/static", StaticFiles(directory="static"), name="static")
images_dir = "static/images"


@app.get("/get-collection/{collection_id}", response_model=GetCollectionSchema)
async def get_collection(
    collection_id: int,
    db: Session = Depends(get_db_fast),
):

    collection_query = (
        db.query(Collection)
        .options(joinedload(Collection.products))
        .filter(Collection.id == collection_id)
        .first()
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

    collections_query = (
        db.query(Collection)
        .options(joinedload(Collection.products))
        .offset(skip)
        .limit(per_page)
        .all()
    )

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
    title: str = Form(),
    db: Session = Depends(get_db_fast),
):
    try:
        input_collection = CreateCollectionSchema(title=title)
    except ValueError as e:
        return {"error": e.errors()[0]["msg"]}

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
    title: str = Form(""),
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

    try:
        input_collection = UpdateCollectionSchema(title=title)
    except ValueError as e:
        return {"error": e.errors()[0]["msg"]}

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


@app.get("/get-product/{product_id}", response_model=GetProductSchema)
async def get_product(product_id: int, db: Session = Depends(get_db_fast)):
    product_query = (
        db.query(Product)
        .options(joinedload(Product.collection))
        .filter(Product.id == product_id)
        .first()
    )

    if product_query is None:
        return JSONResponse(
            {"message": "we do not have such this product with given id"},
            status.HTTP_404_NOT_FOUND,
        )

    return {
        "id": product_query.id,
        "title": product_query.title,
        "price": product_query.price,
        "description": product_query.description,
        "menu": product_query.menu,
        "collection_id": product_query.collection_id,
        "image_path": product_query.image_path,
        "collection_title": product_query.collection.title,
    }


@app.get("/get-all-products", response_model=GetAllProductsSchema)
async def get_all_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(16, le=20),
    db: Session = Depends(get_db_fast),
):
    total_items = db.query(Product).count()
    skip = (page - 1) * per_page

    products_query = (
        db.query(Product)
        .options(joinedload(Product.collection))
        .offset(skip)
        .limit(per_page)
        .all()
    )

    items = []

    for product in products_query:
        product_data = {
            "id": product.id,
            "title": product.title,
            "price": product.price,
            "description": product.description,
            "menu": product.menu,
            "collection_id": product.collection_id,
            "image_path": product.image_path,
            "collection_title": product.collection.title,
        }

        items.append(product_data)

    has_next = (skip + per_page) < total_items
    has_previous = page > 1

    return {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "has_next": has_next,
        "has_previous": has_previous,
        "items": items,
    }


@app.post("/create-product")
async def create_product(
    title: str = Form(""),
    price: int = Form(""),
    description: str = Form(""),
    menu: str = Form(""),
    collection_id: int = Form(""),
    product_image: UploadFile = File(),
    db: Session = Depends(get_db_fast),
):
    try:
        input_product = CreateProductSchema(
            title=title,
            price=price,
            description=description,
            menu=menu,
            collection_id=collection_id,
        )
    except ValueError as e:
        return {"error": e.errors()[0]["msg"]}

    file_location = f"{images_dir}/{product_image.filename}"

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(product_image.file, buffer)

    product_image_path = f"static/images/{product_image.filename}"

    new_product = Product(**input_product.model_dump())
    new_product.image_path = product_image_path

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return JSONResponse(
        {
            "message": f"new product with title of {new_product.title} has been created successfully",
        },
        status.HTTP_201_CREATED,
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
