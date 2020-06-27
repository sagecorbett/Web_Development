from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import csv
import os
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


# Create books table
db.execute("""
    CREATE TABLE books (
        id SERIAL PRIMARY KEY, 
        isbn VARCHAR NOT NULL,
        title VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        year VARCHAR NOT NULL
        )""")


# Create reviews table
db.execute("""
    CREATE TABLE reviews (
        book_id INTEGER REFERENCES books,
        poster_id INTEGER REFERENCES users,
        review VARCHAR NOT NULL,
        rating SMALLINT NOT NULL
    )
""")

# open csv containing 5000 books information
f = open("books.csv")
reader = csv.reader(f)

# insert every book into books table
for isbn, title, author, year in reader:
    db.execute("""
        INSERT INTO books (
            isbn,
            title,
            author,
            year
        ) 
        VALUES (
            :isbn,
            :title,
            :author,
            :year
        )
    """, { "isbn": isbn, "title": title, "author": author, "year": year})



db.commit()
