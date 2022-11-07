from flask import Flask, render_template, request, session, redirect
from user import *
from flask_session import Session
import datetime


app = Flask(__name__)


# Конфигурации сессии
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

GENRES = ["horror", "sci-fi", "thriller", "romance", "classic", "fiction"]

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


@app.route("/login", methods=["POST", "GET"])
def login():

    # Если пользователь уже залогиненный, перенаправление на его личную страничку
    if session.get("email"):
        return redirect("/")

    # Запускается, когда пользователь нажимает Login в навбаре
    if request.form.get("login"):
        return render_template("login.html")

    # Запускается, когда пользователь логиниться
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if get_to_page(email, password):
            # Инициализация пользователя
            session["email"] = request.form.get("email")
            session["cart"] = []
            session["total"] = 0
            return redirect("/")
        else:
            return render_template("login.html", context="Invalid input. Try again")

    # По умолчанию
    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register():
    # Запускается, когда пользователь нажимает Registration в навбаре
    if request.form.get("user_register"):
        surname = request.form.get("surname").strip().lower().capitalize()
        name = request.form.get("name").strip().lower().capitalize()
        email = request.form.get("email").strip().lower()
        password = request.form.get("password")
        phone_number = request.form.get("phone_number").strip()

        if not check_user_input(surname, name, email, password, phone_number):
            return render_template("register.html", context="Invalid input. Try again")

        if check_email(email):
            return render_template("register.html", context="Invalid email. Try again")
        
        if insert_into_db(surname, name, email, password, phone_number):
            return render_template("login.html")
        return render_template("register.html")
    
    # Если пользователь уже залогиненный, перенаправление на его личную страничку
    if session.get("email"):
        return redirect("/")

    # По умолчанию
    return render_template("register.html")


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
        if not check_email(new_email) and not re_test_email(new_email):
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
            