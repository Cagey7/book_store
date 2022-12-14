from flask import Flask, render_template, request, session, redirect, url_for, flash
from user import *
from forms import *
from flask_session import Session
import datetime
import os

SECRET_KEY = os.urandom(32)


app = Flask(__name__)
#app = Flask(__name__,template_folder='../templates')

# Конфигурации сессии
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = SECRET_KEY
Session(app)

GENRES = ["horror", "sci-fi", "thriller", "romance", "classic", "fiction"]

@app.route("/test")
def test():
    return "<h1>Pog</h1>"

@app.route("/", methods=["POST", "GET"])
def index():

    # проверка кнопки на жанр
    chosen_genre = "no_genre"
    for genre in GENRES:
        if request.form.get("genre") == genre:
            chosen_genre = genre

    # получение книг нужного жанра
    book_data = get_book_data(chosen_genre)
    lenth = len(book_data)
    rem = lenth % 3
    return render_template("index.html", book_data=book_data, lenth = lenth, rem = rem)


@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        is_valid = login_check(form.email.data, form.password.data)
        if is_valid:
            session["email"] = form.email.data
            session["cart"] = []
            session["total"] = 0
            return redirect(url_for("login"))
        flash("Wrong email or password", "error")
        return redirect(url_for("login"))


    # Если пользователь уже залогиненный, перенаправление на его личную страничку
    if session.get("email"):
        return redirect(url_for("index"))

    return render_template("login.html", form=form)


@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        surname = form.surname.data.lower().capitalize()
        name = form.name.data.lower().capitalize()
        email = form.email.data.lower()
        password = form.password.data
        phone_number = form.phone_number.data

        if check_email(email):
            flash("Email is already used")
            return redirect(url_for("register"))
        
        if insert_into_db(surname, name, email, password, phone_number):
            return redirect(url_for("login"))
        else:
            flash("Incorrect data")
            return redirect(url_for("register"))
    

    # Если пользователь уже залогиненный, перенаправление на его личную страничку
    if session.get("email"):
        return redirect(url_for("index"))

    return render_template("register.html", form=form)


@app.route("/cart", methods=["POST", "GET"])
def cart():

    if not session.get("email"):
        return redirect("/login")

    # добавление товара в корзину
    if request.form.get("add_to_cart"):
        id = int(request.form.get("id"))
        amount = int(request.form.get("amount"))
        book = get_book(id)
        book_to_cart = {"id": id, "amount": amount, "book": book}

        id_in_session = False
        for i, item in enumerate(session["cart"]):
            if item["id"] == id:
                old_amount = int(session["cart"][i]["amount"])
                session["cart"][i].update({"amount": old_amount+amount})
                id_in_session = True

        if not id_in_session:
            session["cart"].append(book_to_cart)
        
        session["total"] = count_total(session["cart"])
    
    
    # удаление товара из корзины
    if request.form.get("delete_item"):
        id = int(request.form.get("id"))
        for i, item in enumerate(session["cart"]):
            if item["id"] == id:
                session["cart"].pop(i)
        
        session["total"] = count_total(session["cart"])


    if request.form.get("back"):
        return redirect("/")


    total = round(session["total"], 2)
    return render_template("cart.html", total=total)


@app.route("/success", methods=["POST", "GET"])
def success():

    if not session.get("email"):
        return redirect("/login")
    
    # оформление заказа
    if request.form.get("submit_order"):
        # не дает отправить форму повторно
        if session.get("cart") == []:
            return redirect("/")
        
        address = request.form.get("address")
        total_price = float(request.form.get("total"))
        date = str(datetime.datetime.now())
        order_data = (address, total_price, date)

        if address == "":
            return render_template("cart.html", context="Empty address field. Try again")
        
        user_id = get_personal_data(session["email"]).user_id
        if not insert_order(user_id, address, date, total_price):
            print("Error")

        order_id = get_order(user_id).order_id        
        for item in session["cart"]:
            if not insert_purchase(order_id, item["book"].book_id, item["amount"]):
                print("Error")
        
        session["cart"] = []
    
    user_data = get_user_data(session["email"])
    return render_template("success.html", order_data=order_data, user_data=user_data)


@app.route("/personal", methods=["POST", "GET"])
def personal():

    if not session.get("email"):
        return redirect("/login")
    
    # смена почтового адреса
    context = ""
    if request.form.get("change_email"):
        new_email = request.form.get("new_email")
        if check_email(new_email) or not re_test_email(new_email):
            context = "Invalid email. Try again"
        else:
            update_email(get_personal_data(session["email"]).user_id, new_email)
            session["email"] = new_email

    # загрузка информации пользователя
    purchase_data = get_purchase_data(get_personal_data(session["email"]).user_id)
    order_data = get_order_data(get_personal_data(session["email"]).user_id)
    user_data = get_user_data(session["email"])
    return render_template("personal.html", user_data=user_data, purchase_data=purchase_data, order_data=order_data, context=context)


@app.route("/book", methods=["POST", "GET"])
def book():

    if request.args.get("book_info"):
        book_data = get_book(request.args.get("book_info"))

    return render_template("book.html", book_data=book_data)

@app.route("/logout")
def logout():
    session["email"] = None
    session["cart"] = None
    return redirect("/")


@app.route("/remove", methods=["POST", "GET"])
def remove():
    email = session["email"]
    session["email"] = None
    remove_from_db(email)
    return render_template("remove.html", email=email)

@app.route("/searchbook", methods=["POST", "GET"])
def searchbook():

    if request.args.get("search_the_book"):
        book_name = (request.args.get("search_book")).strip().lower().title()
        book_data = get_book_search(book_name)
        if book_data:
            return render_template("book.html", book_data=book_data)
        else:
            return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
