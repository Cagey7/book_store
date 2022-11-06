import hashlib
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.models import *


engine = create_engine("sqlite:///users.db?check_same_thread=False", echo=False)
db = scoped_session(sessionmaker(bind=engine))


def main():
    ...


def insert_into_db(surname, name, email, password, phone_number):
    hashed_password = hash_password(password)
    lower_email = email.lower()
    user = User(surname=surname, name=name, email=lower_email, hashed_password=hashed_password, phone_number=phone_number)
    try:
        db.add(user)
        db.commit()
        return True
    except Exception:
        return False


def get_to_page(email, password):
    hashed_password = hash_password(password)
    lower_email = email.lower()
    try:
        db_hashed_password = db.query(User).filter(User.email == lower_email).one().hashed_password
    except Exception:
        return False
    
    if db_hashed_password == []:
        return False

    if hashed_password == db_hashed_password:
        return True
    return False


def get_personal_data(email):
    personal_data = db.query(User).filter(User.email == email).one()
    return personal_data


def hash_password(password):
    # return hashlib.sha256(password.encode("utf-8")).hexdigest()
    password = password.encode("utf-8")
    hashed_password = hashlib.sha256(password).hexdigest()
    return hashed_password


def check_user_input(surname, name, email, password, phone_number):
    user_data = [surname, name, email, password, phone_number]
    flag = True

    for data in user_data:
        if not re.search(r"^[^ ]{1,30}$", data):
            return False
    return flag


def get_user_data(email):
    return db.query(User).filter(User.email == email).one()


def check_email(email):
    if not re.search(r"^\w+@(\w+\.)?\w+\.\w+$", email, re.IGNORECASE):
        return False
    return True


def remove_from_db(email):
    user_to_delete = db.query(User).filter(User.email == email).one()
    print(user_to_delete)
    db.delete(user_to_delete)
    db.commit()


def insert_book(name, author, genre, year, publisher, discription, price):
    book = Book(name=name, author=author, genre=genre, year=year, publisher=publisher, discription=discription, price=price)
    try:
        db.add(book)
        db.commit()
        return True
    except Exception:
        return False


def get_book_data(genre="no_genre"):
    if genre == "no_genre":
        return db.query(Book).all()
    else:
        return db.query(Book).filter(Book.genre == genre).all()


def get_book(book_id):
    return db.query(Book).filter(Book.book_id == book_id).one()


def get_order_data(user_id):
    return db.query(Order).filter(Order.user_id == user_id).all()


def get_purchase_data(user_id):
    return db.query(Purchase, Book).filter(Order.user_id == user_id).filter(Order.order_id == Purchase.order_id).filter(Purchase.book_id == Book.book_id).all()


def insert_order(user_id, address, date, total_price):
    order = Order(user_id=user_id, address=address, date=date, total_price=total_price)
    try:
        db.add(order)
        db.commit()
        return True
    except Exception:
        return False


def insert_purchase(order_id, book_id, amount):
    purchase = Purchase(order_id=order_id, book_id=book_id, amount=amount)
    try:
        db.add(purchase)
        db.commit()
        return True
    except Exception:
        return False


def get_order(user_id):
    return db.query(Order).filter(Order.user_id == user_id).order_by(Order.order_id.desc()).first()


def update_email(user_id, new_email):
    db.query(User).filter(User.user_id == user_id).update({"email": new_email})
    try:
        db.commit()
        return True
    except Exception:
        return False

def count_total(dict_cart):
    total = 0
    for item in dict_cart:
        total += item["amount"] * item["book"].price
    return round(total, 2)


if __name__ == "__main__":
    main()


