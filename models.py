from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from database import Base


class Author(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)          
    name = Column(String(150), nullable=False)      
    country = Column(String(100), nullable=True)    
    books = relationship("Book", back_populates="author")


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    year = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)

    author = relationship("Author", back_populates="books")

    __table_args__ = (
        CheckConstraint("price > 0", name="ck_book_price"),
        CheckConstraint("quantity >= 0", name="ck_book_quantity"),
        CheckConstraint("year > 0", name="ck_book_year"),
    )
