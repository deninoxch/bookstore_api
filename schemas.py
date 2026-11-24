from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _not_blank(value: str) -> str:
    v = value.strip()
    if not v:
        raise ValueError("не должно быть пустым или состоять из одних пробелов")
    return v



class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    country: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        return _not_blank(v)

    @field_validator("country")
    @classmethod
    def country_not_blank(cls, v: str | None) -> str | None:
        return None if v is None else _not_blank(v)


class AuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    country: str | None



class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    year: int = Field(gt=0)
    quantity: int = Field(ge=0)
    author_id: int = Field(gt=0)  

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        return _not_blank(v)


class BookRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    price: Decimal
    year: int
    quantity: int
    author_id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    year: int | None = Field(default=None, gt=0)
    quantity: int | None = Field(default=None, ge=0)

    @field_validator("title", "price", "year", "quantity")
    @classmethod
    def required_not_null(cls, v, info):

        if v is None:
            raise ValueError(f"поле '{info.field_name}' нельзя обнулить через null")
        return v

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        return None if v is None else _not_blank(v)
