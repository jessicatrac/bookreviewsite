import os, requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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
def index():
    return render_template("login.html")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/re_login", methods=['POST'])
def re_login():
	username_new = request.form.get("username")
	password_new = request.form.get("password")
	try:
		db.execute("INSERT INTO users (username, password) VALUES (:user, :pass)",
			{"user": username_new, "pass": password_new})
		db.commit()
		print("Registered %s to the database" % username_new)
	except ValueError:
		return render_template("error.html", message="Sorry - cannot register user.")
	return render_template("login.html")

@app.route("/sign", methods=['POST'])
def sign():
	username_attempt = request.form.get("username")
	password_attempt = request.form.get("password")
	try:
		user_match = db.execute("SELECT * FROM users WHERE username=:username", {"username": username_attempt}).fetchone()
	except ValueError:
		return render_template("error.html", message="Sorry - we couldn't find you in our system. Please return to try again or register!")
	if user_match.password == password_attempt:
		session['user'] = user_match.username
		return render_template("search.html", name=session.get('user'))
	else:
		return render_template("error.html", message="Sorry - we couldn't find you in our system. Please return to try again or register!")

@app.route("/search")
def search():
	return render_template("search.html")

@app.route("/book_results", methods=['POST'])
def book_results():
	user_search_key = '%' + request.form.get("user_search_key") + '%'
	books_list = db.execute("SELECT * FROM books WHERE isbn LIKE :isbn OR author LIKE :author OR title LIKE :title", 
		{"isbn":user_search_key, "author":user_search_key, "title":user_search_key}).fetchall()
	for books in books_list:
		print("Search result: %s" % books.title)
	if books_list is None:
		return render_template("error.html", message = "Sorry - no books found.")
	else:
		return render_template("all_book_results.html",books_list=books_list)


@app.route("/bookpage/<string:isbn_search>")
def bookpage(isbn_search):
	book_search = db.execute("SELECT * FROM books WHERE isbn =:isbn_search", {"isbn_search": isbn_search}).fetchone()
	if book_search is None: 
		return render_template("error.html", message = "Sorry - this book does not exist.")
	book_review_data = requests.get("https://www.goodreads.com/book/review_counts.json", 
		params={"key": "0z74opx09u94JjbpeeUWg", "isbns": isbn_search})
	book_review = book_review_data.json()
	book_avg_rating = book_review["books"][0]["average_rating"]
	book_review_count = book_review["books"][0]["work_ratings_count"]
	return render_template("bookpage.html", book = book_search, book_avg_rating=book_avg_rating, book_review_count=book_review_count)

@app.route("/review_submission", methods=['POST'])
def review_submission():
	user_rating = request.form.get("user_rating")
	user_comments = request.form.get("user_comments")
	return render_template("review_submission.html", user_rating=user_rating, user_comments=user_comments)

