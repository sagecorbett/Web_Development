import os

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from werkzeug.security import generate_password_hash, check_password_hash

from helper_functions import login_required

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    if session.get("user_id") is None:
        return redirect("/login")
    else:
        return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any current sessions
    session.clear()

    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if not password or not username:
            return render_template("login.html")

        user = db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}).fetchone()
        db.commit()

        if not check_password_hash(user.password, password):
            return render_template("login.html")
        else:
            session["user_id"] = user.id
            return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    if not password or not username:
        return redirect('/login')
    confirm_password = request.form.get("confirm")

    # Check if password and confirm password do not match
    if confirm_password != password:
        return redirect('/login')

    # Hash the password before storing it's hash in the user table
    hash_password = generate_password_hash(password)
    db.execute(
        "INSERT INTO users ( username, password ) VALUES (:username, :password)",
        {"username": username, "password": hash_password})

    # Get the User id of the newly created user and add it to the session so that the user is "logged in"
    user = db.execute("SELECT id FROM users WHERE username = :username", {
                        "username": username}).fetchone()
    session["user_id"] = user.id
    db.commit()
    return redirect("/")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    # Clear any user session data
    session.clear()
    return redirect('/login')


@app.route("/search", methods=["GET"])
@login_required
def search():
    search_by = request.args.get("search_by")
    search = request.args.get("search")
    if not search_by or not search:
        return redirect("/")

    else:
        results = db.execute(f"SELECT * FROM books WHERE {search_by} ILIKE :search  ORDER BY title ASC", {
                             "search_by": search_by, "search": search + '%'}).fetchall()
        print(len(results))
        return render_template("results.html", data=results, results=len(results), search=search)


@app.route("/book", methods=["GET", "POST"])
@login_required
def book():
    if request.method == "GET":
        # Queries needed for this page
        book_id = request.args.get("book_id")
        book_query = db.execute(
            "SELECT * FROM books WHERE id = :id", {"id": book_id}).fetchone()
        review_query = db.execute("""
                SELECT 
                    review, 
                    rating,
                    username
                FROM reviews
                JOIN users ON users.id = reviews.poster_id
                WHERE book_id = :id
            """, {"id": book_id}).fetchall()

        # Get goodreads rating for this book
        goodreads_rating = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "H3lH3PbpVLDNRmlKuga6VA", "isbns": book_query.isbn })

        return render_template("book.html", book=book_query, reviews=review_query, goodread=goodreads_rating.json()["books"][0])

    elif request.method == "POST":
        rating = request.form.get("rating")
        review = request.form.get("review")
        book = request.form.get("book-id")
        if not rating or not review:
            return render_template("error.html")
        else:
            # Check the data base if the user has posted a review for this book before
            user_has_posted_before = db.execute("""
                SELECT * FROM reviews
                WHERE poster_id = :user_id
                AND book_id = :book_id
            """, { "book_id": book, "user_id": session["user_id"]}).fetchone()
            if user_has_posted_before:
                return redirect(f"/book?book_id={book}")
            db.execute("""
                INSERT INTO reviews (
                    book_id,
                    poster_id,
                    review,
                    rating
                ) 
                VALUES (
                    :book_id,
                    :poster_id,
                    :review,
                    :rating
                )
            """, {"book_id": book, "poster_id": session["user_id"], "review": review, "rating": rating})
            db.commit()
            return redirect(f"/book?book_id={book}")



@app.route('/api/<string:isbn>', methods=["GET"])
def api(isbn):
    if request.method == "GET":
        book_rating = requests.get("https://www.goodreads.com/book/review_counts.json",
                        params={"key": "H3lH3PbpVLDNRmlKuga6VA", "isbns": isbn}).json()["books"][0]

        book_info = db.execute("""
            SELECT * FROM books
            WHERE isbn = :isbn
        """, {"isbn": isbn}).fetchone()
        
        print(book_rating)
        return jsonify({
            "title": book_info.title,
            "author": book_info.author,
            "year": book_info.year,
            "isbn": isbn,
            "review_count": book_rating["reviews_count"],
            "average_score": book_rating["average_rating"] 
        })
