import json

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session

from cache import CACHE_KEY, CACHE_TTL, cache_delete, cache_get, cache_setex
from database import Base, engine, get_db
from models import Author, Book
from schemas import AuthorCreate, AuthorRead, BookCreate, BookRead, BookUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="BookStore API")



@app.post("/authors", response_model=AuthorRead, status_code=201)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    author = Author(name=data.name, country=data.country)
    db.add(author)
    db.commit()
    db.refresh(author)  # подтягиваем id, сгенерированный PostgreSQL
    return author


@app.get("/authors", response_model=list[AuthorRead])
def list_authors(db: Session = Depends(get_db)):
    return db.query(Author).order_by(Author.id).all()


@app.get("/authors/{author_id}/books", response_model=list[BookRead])
def get_author_books(author_id: int, db: Session = Depends(get_db)):
    author = db.get(Author, author_id)
    if author is None:
        raise HTTPException(status_code=404, detail="Автор не найден")
    return author.books



@app.post("/books", response_model=BookRead, status_code=201)
def create_book(data: BookCreate, db: Session = Depends(get_db)):
    if db.get(Author, data.author_id) is None:
        raise HTTPException(status_code=404, detail="Автор не найден")

    book = Book(**data.model_dump())
    db.add(book)
    db.commit()
    db.refresh(book)

    cache_delete(CACHE_KEY)  
    return book


@app.get("/books", response_model=list[BookRead])
def list_books(
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if search:
        return (
            db.query(Book)
            .filter(Book.title.ilike(f"%{search}%"))
            .order_by(Book.id)
            .all()
        )

    cached = cache_get(CACHE_KEY)
    if cached is not None:
        print("CACHE HIT")
        return json.loads(cached)  

    print("CACHE MISS")
    books = db.query(Book).order_by(Book.id).all()

    payload = json.dumps(
        [BookRead.model_validate(b).model_dump(mode="json") for b in books]
    )
    cache_setex(CACHE_KEY, CACHE_TTL, payload)
    return books


@app.get("/books/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")
    return book


@app.patch("/books/{book_id}", response_model=BookRead)
def update_book(book_id: int, data: BookUpdate, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)

    cache_delete(CACHE_KEY)
    return book


@app.delete("/books/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if book is None:
        raise HTTPException(status_code=404, detail="Книга не найдена")

    db.delete(book)
    db.commit()

    cache_delete(CACHE_KEY)
