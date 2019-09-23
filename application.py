import os

import requests

from flask import Flask, render_template, request, redirect, session, url_for, jsonify, abort
from flask_session import Session
from itsdangerous import want_bytes
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL") or not os.getenv("GOODREADS_KEY"):
    raise RuntimeError("DATABASE_URL and/or GOODREADS_KEY is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Create login required decorator for pages that require user login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email")
        if not username_or_email: 
            error = "Enter username / email"
            return render_template("login.html", error=error)

        password = request.form.get("password")
        if not password: 
            error = "Enter password"
            return render_template("login.html", error=error)

        user = db.execute("SELECT user_id, password FROM users "
                            + "WHERE username = :username_or_email "
                            + "OR email = :username_or_email",
                            {'username_or_email':username_or_email}).fetchone()
        if not user or not check_password_hash(user.password, password):
            error = "Invalid username/password combo"
            return render_template("login.html", error=error)

        session.clear()
        session['user_id'] = user.user_id
        return redirect("/")

    return render_template("login.html")


@app.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation_password = request.form.get("confirmation_password")
        email = request.form.get("email")

        if not username or not password or not confirmation_password or not email:
            error = "Please complete all requested fields"
            return render_template("register.html", error=error)
        elif not password == confirmation_password:
            error = "Password and confirmation don't match"
            return render_template("register.html", error=error)
        elif not db.execute("SELECT * FROM users WHERE username = :username",
                            {'username':username}).rowcount == 0:
            error = "User already exists"
            return render_template("register.html", error=error)

        session.clear()
        hashed_password = generate_password_hash(password)
        db.execute("INSERT INTO users (username, password, email) "
                    + "VALUES (:username, :hashed_password, :email)",
                    {'username': username, 'hashed_password': hashed_password, 'email': email}) 
        db.commit()
        user = db.execute("SELECT user_id, password FROM users "
                            + "WHERE username = :username",
                            {'username': username}).fetchone()
        session['user_id'] = user.user_id
        return redirect("/")

    return render_template("register.html") 


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logged_out.html")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/search", methods=("GET", "POST"))
@login_required
def search():
    if request.method == "POST":  
        search = "%" + request.form.get("book_search") + "%"
        books = db.execute("SELECT isbn, title, author, year FROM books "
                            + "WHERE LOWER(isbn) LIKE LOWER(:search) "
                            + "OR LOWER(title) LIKE LOWER(:search) "
                            + "OR LOWER(author) LIKE LOWER(:search) "
                            + "LIMIT 30", {'search':search}).fetchall()
        print(type(books))
        return render_template("search.html", books=books)

    return redirect("/")


@app.route("/book/<string:isbn>", methods=('GET', 'POST'))
@login_required
def book(isbn):
    
    error = None

    if request.method == "POST":
        review = request.form.get("review")
        rating = request.form.get("rating")
        if not review:
            error = "Please submit a review"
        elif not rating:
            error = "Please submit a rating"
        else:
            db.execute("insert into reviews (user_id, isbn, rating, review) " 
                        + "values (:user, :isbn, :rating, :review)",
                        {'user':session['user_id'], 'isbn':isbn, 
                        'rating':rating, 'review':review})
            db.commit()

    # Collect all book info from books DB
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                        {'isbn': isbn}).fetchone()

    # Get requred ratints info from goodreads
    key = os.getenv("GOODREADS_KEY")
    goodreads_info = requests.get("https://www.goodreads.com/book/review_counts.json", 
                            params={"key": key, "isbns": isbn}).json()['books'][0]
    avg_gr_rating = goodreads_info['average_rating']
    total_gr_ratings = goodreads_info['work_ratings_count']

    # Get review info from reviews DB
    user_review = db.execute("SELECT * FROM reviews "
                             + "WHERE user_id = :user "
                             + "AND isbn = :isbn",
                             {'user': session['user_id'], 'isbn': isbn}).fetchone()
    other_reviews = db.execute("SELECT username, review, rating FROM reviews "
                                + "JOIN users ON reviews.user_id = users.user_id "
                                + "WHERE isbn = :isbn " 
                                + "AND reviews.user_id != :user",
                                {'user': session['user_id'], 'isbn': isbn}).fetchall ()
    avg_user_rating = db.execute("SELECT AVG(rating) FROM reviews "
                                    + "WHERE isbn = :isbn",
                                    {'isbn': isbn}).fetchone()

    if avg_user_rating.avg:
        avg_user_rating = round(avg_user_rating.avg,2)

    return render_template("book.html", 
                              book=book, 
                              avg_gr_rating=avg_gr_rating,
                              total_gr_ratings=total_gr_ratings,
                              user_review=user_review, 
                              other_reviews=other_reviews, 
                              avg_user_rating = avg_user_rating,
                              error=error)


@app.route("/edit_review/<string:isbn>", methods=("GET", "POST"))
@login_required
def edit_review(isbn):

    error = None

    if request.method == "POST":
        review = request.form.get("review")
        rating = request.form.get("rating")
        if not review:
            error = "Please submit a new review"
        elif not rating:
            error = "Please submit a new rating"
        else:
            db.execute("UPDATE reviews SET review = :review, rating = :rating "
                        + "WHERE user_id = :user "
                        + "AND isbn = :isbn",
                        {'review': review, 'rating': rating,
                        'user': session['user_id'], 'isbn': isbn})
            db.commit()
            return redirect(url_for('book', isbn=isbn))

    key = os.getenv("GOODREADS_KEY")
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                        {'isbn': isbn}).fetchone()
    goodreads_info = requests.get("https://www.goodreads.com/book/review_counts.json", 
                                    params={"key": key, "isbns": isbn}).json()['books'][0]
    avg_rating = goodreads_info['average_rating']
    ratings = goodreads_info['work_ratings_count']
    user_review = db.execute("SELECT * FROM reviews "
                                + "WHERE user_id = :user "
                                + "AND isbn = :isbn",
                                {'user': session['user_id'], 'isbn': isbn}).fetchone()
     
    return render_template("edit_review.html", 
                                book=book, 
                                avg_rating=avg_rating, 
                                ratings=ratings, 
                                user_review=user_review,
                                error = error)


@app.route("/api/<string:isbn>", methods=("GET", "POST"))
def api(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn",
                        {'isbn': isbn}).fetchone()
    if not book:
        return jsonify({"error": "ISBN not found"}), 404
    avg_rating = db.execute("SELECT AVG(rating) FROM reviews "
                            + "WHERE isbn = :isbn",
                            {'isbn': isbn}).fetchone()
    review_count = db.execute("SELECT COUNT(*) FROM reviews "
                                + "WHERE isbn = :isbn",
                                {'isbn': isbn}).fetchone()
    api_info = {"title": book.title, 
                    "author": book.author, 
                    "year": book.year, 
                    "isbn": isbn, 
                    "review_count": review_count.count, 
                    "average_score": float(avg_rating.avg)}
    return jsonify(api_info)