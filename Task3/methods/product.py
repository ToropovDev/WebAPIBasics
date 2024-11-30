from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Task3.db.base import get_db
from Task3.db.models import Product
from Task3.utils import scrape_category

router = APIRouter()


@router.post("/parse/")
def parse_section(url: str, db: Session = Depends(get_db)):
    if not url.startswith("https://www.maxidom.ru/catalog/"):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        products, section_name = scrape_category(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    for product in products:
        db_product = Product(
            name=product["name"], price=product["price"], section=section_name
        )
        db.add(db_product)

    db.commit()
    return {
        "message": f"Parsed and added {len(products)} products from section '{section_name}'."
    }


@router.get("/product/")
def get_product_by_name(name: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


@router.get("/section/")
def get_products_by_section(url: str, db: Session = Depends(get_db)):
    if not url.startswith("https://www.maxidom.ru/catalog/"):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        products, section_name = scrape_category(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    db_products = db.query(Product).filter(Product.section == section_name).all()
    if not db_products:
        for product in products:
            db_product = Product(
                name=product["name"], price=product["price"], section=section_name
            )
            db.add(db_product)
        db.commit()
        db_products = db.query(Product).filter(Product.section == section_name).all()

    return db_products


@router.put("/product/")
def update_product_price(name: str, new_price: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    product.price = new_price
    db.commit()
    return {
        "message": f"Updated product '{product.name}' with new price '{new_price}'."
    }


@router.delete("/product/")
def delete_product_by_name(name: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    db.delete(product)
    db.commit()
    return {"message": f"Product '{name}' has been deleted."}


@router.delete("/section/")
def delete_products_by_section(url: str, db: Session = Depends(get_db)):
    if not url.startswith("https://www.maxidom.ru/catalog/"):
        raise HTTPException(status_code=400, detail="Invalid URL format.")

    try:
        _, section_name = scrape_category(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    products_in_section = (
        db.query(Product).filter(Product.section == section_name).all()
    )
    if not products_in_section:
        raise HTTPException(
            status_code=404, detail=f"No products found in section '{section_name}'."
        )

    for product in products_in_section:
        db.delete(product)

    db.commit()
    return {"message": f"All products in section '{section_name}' have been deleted."}
