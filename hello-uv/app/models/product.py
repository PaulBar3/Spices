from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class ProductBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = Field(default=None, max_length=500)


class Product(ProductBase, table=True):
    __tablename__ = "products"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, min_length=1, max_length=2000)
    price: Optional[float] = Field(default=None, gt=0)
    image_url: Optional[str] = Field(default=None, max_length=500)
