from fastapi import FastAPI
from Task3.db.base import Base, engine
from Task3.methods.product import router as product_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(product_router, prefix="/product", tags=["product"])
