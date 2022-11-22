import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
import re
import random

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

connection = psycopg2.connect(user="dstruble",
                                  password="dan112",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="dstruble")
cursor = connection.cursor()
print 

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database

# Make sure API key is set
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":
        user = session.get("user_id")
        cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
        rows = cursor.fetchall()
        total = len(rows)
        option = random.random()
        meal_number = total * option
        meal_number = int(meal_number)
        meal = rows[meal_number]
        return render_template("index.html", meal=meal)
    else:
        meal=["", ""]
        return render_template("index.html", meal=meal)

@app.route("/meals", methods=["GET", "POST"])
@login_required
def meals():
    """Add meal to the Menu"""
    if request.method == "POST":
        user = session.get("user_id")
        mealname = request.form.get("mealname")
        dad_eats = request.form.get("dadeats")
        if not dad_eats:
            dad_eats = False
        else:
            dad_eats = True
        kids_eat = request.form.get("kids_eat")
        if not kids_eat:
            kids_eat = False
        else:
            kids_eat = True
        red_sauce = request.form.get("red_sauce")
        if not red_sauce:
            red_sauce = False
        else:
            red_sauce = True
        meat = request.form.get("meat")
        if not meat:
            meat = False
        else:
            meat = True
        cheese = request.form.get("cheese")
        if not cheese:
            cheese = False
        else:
            cheese = True
        unhealthy = request.form.get("unhealthy")
        if not unhealthy:
            unhealthy = False
        else:
            unhealthy = True
        fiber = request.form.get("fiber")
        if not fiber:
            fiber = False
        else:
            fiber = True
        day = request.form.get("day")
        if day == "None":
            day = "Any"

        if not mealname:
            return apology(message="Missing name", code=403)
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if regex.search(mealname) != None:
            return apology(message="No special characteres please")
        u = cursor.execute("SELECT * from meals where user_id = %s and mealname = %s", (session.get("user_id"), request.form.get("mealname"),))
        rows = cursor.fetchone()
        if rows:
            cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
            meals = cursor.fetchall()
            return render_template("meals.html", message="Meal name taken", meals=meals)
        else:
            cursor.execute("INSERT INTO meals (mealname, kids_eat, dad_eats, red_sauce, meat, cheese, unhealthy, fiber, day, user_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (mealname, kids_eat, dad_eats, red_sauce, meat, cheese, unhealthy, fiber, day, user))
            connection.commit()
            cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
            meals = cursor.fetchall()
            yes = ["Meal added to the menu!", "Yes"]
            success = yes[0]
            return render_template("meals.html", success=success, meals=meals)

    else:
        user = session.get("user_id")
        cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
        meals = cursor.fetchall()
        return render_template("meals.html", meals=meals)

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        meal_id = request.form.get("meal_id")
        print(meal_id, flush=True)
        user = session.get("user_id")
        cursor.execute("DELETE FROM meals WHERE user_id = %s AND meal_id = %s", (user, meal_id,))
        connection.commit()
        no = ["Deleted the meal", "There was an error"]
        cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
        meals = cursor.fetchall()
        return render_template("meals.html", no=no, meals=meals)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        name = request.form.get("username")
        # Query database for username
        cursor.execute("SELECT * FROM users WHERE username = %s;", (name,))
  
        rows = cursor.fetchone()
        print(rows[0], flush=True)
        # Ensure username exists and password is correct
        if rows is None:
            return apology("invalid username and/or password", 403)
        if rows is not None:
            if not check_password_hash(rows[2], request.form.get("password")):
                return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
    # Validate username missing
        name = request.form.get("username")
        if not name:
            return apology(message="Missing name", code=403)
        passw = request.form.get("password")
        conf = request.form.get("confirmation")
        if not passw:
            return apology(message="Provide password", code=403)
        if not conf:
            return apology(message="Provide password", code=403)
        if conf != passw:
            return apology(message="Password mismatch", code=403)
        # Validate username doesn't exist
        u = cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username")))


        if u != None:
            return apology(message="Username taken", code=403)

        # Store username and password
        hash = generate_password_hash(passw)
        cursor.execute("INSERT INTO users (username, password) VALUES(%s, %s)", (name, hash))
        connection.commit()
        return redirect("/login")
    else:
        return render_template("register.html")

