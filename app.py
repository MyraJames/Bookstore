from flask import Flask, request, jsonify  
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS 
import os


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.sqlite" )

db = SQLAlchemy(app)
ma = Marshmallow(app)
CORS(app)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, unique=True, nullable=False)
    author = db.Column(db.String, nullable=False)
    review = db.Column(db.String(200))
    

    def __init__(self, title, author, review):
        self.title = title
        self.author = author
        self.review = review

class BookSchema(ma.Schema):
    class Meta:
        fields = ("id", "title", "author", "review")


book_schema = BookSchema()
multiple_books_schema = BookSchema(many=True)
 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)
    #unique=False is a default, nullable=True is also a default

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "username", "email")

user_schema = UserSchema()
multiple_users_schema = UserSchema(many=True)

@app.route("/book/add", methods=["POST"])
def add_book():
    print("test")
    if request.content_type != "application/json":
        print("test two")
        return "Error: Data must be sent as JSON."
    
    post_data = request.get_json()
    print(post_data)
    title = post_data.get("title")
    author = post_data.get("author")
    review = post_data.get("review")

    record = Book(title, author, review)
    db.session.add(record)
    db.session.commit()

    return jsonify("Data added successfully")

@app.route("/book/get", methods=["GET"])
def get_all_books():
    all_books = db.session.query(Book.id, Book.title, Book.author, Book.review).all()
    return jsonify(all_books)

@app.route("/book/get/<id>", methods=["GET"])
def get_one_book(id):
    one_book = db.session.query(Book.id, Book.title, Book.author, Book.review).filter(Book.id == id).first() #function to get one book
    return jsonify(one_book)


@app.route("/book/get/marshmallow", methods=["GET"])
def get_all_books_marshmallow():
    # all_books = Book.query.all() #can use either this or syntax below both will work
    all_books = db.session.query(Book).all()
    return jsonify(multiple_books_schema.dump(all_books))


@app.route("/book/get/marshmallow/<id>", methods=["GET"])
def get_one_book_marshmallow(id):
    # one_book = Book.query.get(id)
    one_book = db.session.query(Book).filter(Book.id == id).first()

    # one_book_schema = {}
    # one_book_schema["id"] = one_book.id
    # one_book_schema["title"] = one_book.title
    # one_book_schema["author"] = one_book.author
    # one_book_schema["review"] = one_book.review
    # return jsonify(one_book_schema)

    return jsonify(book_schema.dump(one_book))

@app.route("/book/update/<old_title>", methods=["PUT"])
def update_book(0ld_title):
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."

    put_data = request.get_json()
    title = put_data.get("title")
    author = put_data.get("author")
    review = put_data.get("review")

    record = db.session.query(Book).filter(Book.title == old_title).first()

    if title is not None:
        record.title = title
    if author is not None:
        record.author = author
    if review is not None:
        record.review = review


    db.session.commit()
    return jsonify("Data updated successfully")


@app.route("/book/delete/<title>", methods=["DELETE"])
def delete_book_by_title(title):
    record = db.session.query(Book).filter(Book.title == title).first()
    if record is None:
        return jsonify(f"Book with title {title} doesn't exist")

    db.session.delete(record)
    db.session.commit()
    return jsonify(f"Book with title{title} was successfully deleted")



   


@app.route("/user/add", methods=["POST"])
def add_user():
    if request.content_type != "application/json":
        return "Error: Data must be sent as JSON."
    
    post_data = request.get_json()
    username = post_data.get("username")
    password = post_data.get("password")
    email = post_data.get("email")

    record = User(username, password, email)
    db.session.add(record)
    db.session.commit()

    return jsonify("Data added successfully")


@app.route("/user/get", methods=["GET"])
def get_all_users():
    all_users = db.session.query(User).all()
    return jsonify(multiple_users_schema.dump(all_users))


@app.route("/user/get/<id>", methods=["GET"])
def get_one_user(id):
    one_user = db.session.query(User).filter(User.id == id).first()
    return jsonify(user_schema.dump(one_user))


@app.route("/user/book/<user_id>/<book_id>", methods=["GET"])
def get_one_user_and_one_book(user_id, book_id):
    user = db.session.query(User).filter(User.id == user_id).first()
    book = db.session.query(Book).filter(Book.id == book_id).first()
    result = [user_schema.dump(user), book_schema.dump(book)]
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)