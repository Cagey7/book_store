from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    surname = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    hashed_password = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)


class Book(db.Model):
    __tablename__ = "books"
    book_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    author = db.Column(db.String)
    genre = db.Column(db.String)
    year = db.Column(db.Integer)
    publisher = db.Column(db.String)
    discription = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    address = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=False)
    total_price = db.Column(db.Float, nullable=False)


class Purchase(db.Model):
    __tablename__ = "purchases"
    purchase_id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.order_id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    orders = db.relationship("Order", backref="purchase", lazy=True)

