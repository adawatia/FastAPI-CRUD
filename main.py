from typing import Annotated
from fastapi import FastAPI, HTTPException, status, Path
from pydantic import BaseModel, Field

app = FastAPI(title="Product API", version="1.1.0")


# ------------------ MODELS ------------------
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    description: str | None = Field(None, max_length=255, description="Product description")
    price: float = Field(..., gt=0, description="Product price")
    quantity: int = Field(..., ge=0, description="Available stock quantity")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating (partial allowed)"""
    name: str | None = None
    description: str | None = None
    price: float | None = Field(None, gt=0)
    quantity: int | None = Field(None, ge=0)


class Product(ProductBase):
    id: int


# ------------------ FAKE DB ------------------
products: list[Product] = [
    Product(id=1, name="Phone", description="A smartphone", price=699.99, quantity=50),
    Product(id=2, name="Laptop", description="A powerful laptop", price=999.99, quantity=30),
    Product(id=3, name="Pen", description="A blue ink pen", price=1.99, quantity=100),
    Product(id=4, name="Table", description="A wooden table", price=199.99, quantity=20),
]

_next_id = len(products) + 1


# ------------------ ENDPOINTS ------------------
@app.get("/", response_model=str, summary="Greeting endpoint")
async def greet() -> str:
    return "Hello world"


@app.get("/products/", response_model=list[Product], summary="Get all products")
async def get_all_products() -> list[Product]:
    return products


@app.get(
    "/products/{product_id}",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
    summary="Get product by ID",
)
async def get_product_by_id(
    product_id: Annotated[int, Path(gt=0, description="The ID of the product")]
) -> Product:
    for product in products:
        if product.id == product_id:
            return product
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@app.post(
    "/products/",
    response_model=Product,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
)
async def create_product(product_data: ProductCreate) -> Product:
    global _next_id
    product = Product(id=_next_id, **product_data.dict())
    products.append(product)
    _next_id += 1
    return product


@app.put(
    "/products/{product_id}",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
    summary="Replace a product (full update)",
)
async def replace_product(
    product_id: Annotated[int, Path(gt=0)], product_data: ProductCreate
) -> Product:
    for i, existing in enumerate(products):
        if existing.id == product_id:
            updated = Product(id=product_id, **product_data.dict())
            products[i] = updated
            return updated
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@app.patch(
    "/products/{product_id}",
    response_model=Product,
    responses={404: {"description": "Product not found"}},
    summary="Partially update a product",
)
async def update_product(
    product_id: Annotated[int, Path(gt=0)], product_data: ProductUpdate
) -> Product:
    for i, existing in enumerate(products):
        if existing.id == product_id:
            updated_fields = product_data.dict(exclude_unset=True)
            updated = products[i].copy(update=updated_fields)
            products[i] = updated
            return updated
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@app.delete(
    "/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Product not found"}},
    summary="Delete a product",
)
async def delete_product(product_id: Annotated[int, Path(gt=0)]) -> None:
    for i, existing in enumerate(products):
        if existing.id == product_id:
            del products[i]
            return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
