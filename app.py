import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
import psycopg2
import re
import random
from oauthlib.oauth2 import WebApplicationClient
import requests
import json

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

#Configure for Google Login
# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

#Configure email
mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": os.environ['MAIL_USERNAME'],
    "MAIL_PASSWORD": os.environ['MAIL_PASSWORD']
}
app.config.update(mail_settings)
mail = Mail(app)

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
#@login_required
def index():
    if 'user_id' in session:
        if request.method == "POST":
            user = session.get("user_id")
            cursor.execute("SELECT meals_id, mealname, rules FROM meals where user_id = %s", (user,))
            rows = cursor.fetchall()

            # find meals that have rules, need to cut those out of options
            rules = request.form.getlist('rule') #[2, 3]
            if rules:
            #rows[2] = [2,3,4]
                new_meal = {}
                count = cursor.rowcount
                meal_counter = 0
                count_rules = cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
                count_rules = cursor.rowcount
                print(count_rules, flush=True)
                count_selected_rules = len(rules)
                print(count_selected_rules, flush=True)
                if count_rules == count_selected_rules:
                    for x in range(count):
                        if set(rules) == set(rows[x][2]):
                            new_meal[meal_counter] = rows[x][1]
                            meal_counter += 1    
                else:
                    for x in range(count):
                        if set(rules) & set(rows[x][2]):
                            new_meal[meal_counter] = rows[x][1]
                            meal_counter += 1
                
                if meal_counter !=0:
                    total = meal_counter
                    print(total, flush=True)
                    option = random.random()
                    print(option, flush=True)
                    meal_number = total * option
                    print(meal_number, flush=True)
                    meal_number = int(meal_number)
                    print(meal_number, flush=True)
                    meal = new_meal[meal_number]
                else:
                    meal="No Match!"
            else:
                new_meal = rows
                total = len(new_meal)
                option = random.random()
                meal_number = total * option
                meal_number = int(meal_number)
                meal = new_meal[meal_number][1]
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            return render_template("index.html", meal=meal, rules=rules)
        else:
            meal=""
            user = session.get("user_id")
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            return render_template("index.html", meal=meal, rules=rules)
    else:
        return render_template("storefront.html")

@app.route("/storefront")
def storefront():
    return render_template("storefront.html")

@app.route("/meals", methods=["GET", "POST"])
@login_required
def meals():
    """Add meal to the Menu"""
    if request.method == "POST":
        user = session.get("user_id")
        mealname = request.form.get("mealname")
        if not mealname:
            return apology(message="Missing name", code=403)
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if regex.search(mealname) != None:
            return apology(message="No special characteres please")
        rules = request.form.getlist('rule')
        
        u = cursor.execute("SELECT * from meals where user_id = %s and mealname = %s", (session.get("user_id"), request.form.get("mealname"),))
        rows = cursor.fetchone()
        # check if the meal name exists
        if rows:
            cursor.execute("SELECT meals_id, mealname, rules FROM meals where user_id = %s", (user,))
            meals = cursor.fetchall()
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            return render_template("meals.html", message="Meal name taken", meals=meals, rules=rules)
        else:
            cursor.execute("INSERT INTO meals (mealname, rules, user_id) VALUES(%s, %s, %s)", (mealname, rules, user))
            connection.commit()
            cursor.execute("SELECT meals_id, mealname, rules FROM meals where user_id = %s", (user,))
            meals = cursor.fetchall()
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            success = "Meal added to the menu!"
            return render_template("meals.html", success=success, meals=meals, rules=rules)

    else:
        user = session.get("user_id")
        cursor.execute("SELECT meals_id, mealname, rules FROM meals where user_id = %s", (user,))
        meals = cursor.fetchall()
        cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
        rules = cursor.fetchall()
        return render_template("meals.html", meals=meals, rules=rules)

@app.route("/rules", methods=["GET", "POST"])
@login_required
def rules():
    """Add rule to the Rules"""
    if request.method == "POST":
        user = session.get("user_id")
        rule = request.form.get("rulename")
        if not rule:
            return apology(message="Please enter a rule name")
        value = True
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        if regex.search(rule) != None:
            return apology(message="No special characters please")
        u = cursor.execute("SELECT * from rules where user_id = %s and rule_name = %s", (session.get("user_id"), request.form.get("rulename"),))
        rows = cursor.fetchone()
        if rows:
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            return render_template("rules.html", message="Rule name taken", rules=rules)
        else:
            cursor.execute("INSERT INTO rules (rule_name, value, user_id) VALUES(%s, %s, %s)", (rule, value, user))
            connection.commit()
            cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
            rules = cursor.fetchall()
            yes = ["Meal added to the menu!", "Yes"]
            success = yes[0]
            return render_template("rules.html", success=success, rules=rules)

    else:
        user = session.get("user_id")
        cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
        rules = cursor.fetchall()
        return render_template("rules.html", rules=rules)

@app.route("/deleterule", methods=["GET", "POST"])
@login_required
def deleterule():
    if request.method == "POST":
        rule_id = request.form.get("rule_id")
        print(rule_id, flush=True)
        user = session.get("user_id")
        # need to look at what meals have these rules and delete the rules from those meals
        # get meals for the user, look for the difference, update meal rules w/ those new rules
        cursor.execute("SELECT rule_name from rules where user_id = %s and rule_id = %s", (user, rule_id,))
        rule_name = cursor.fetchall()
        
        print(rule_name[0][0], flush=True)
        cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
        meal_rules = cursor.fetchall()
        print(meal_rules[0][2], flush=True)
        count = cursor.rowcount
        for x in range(count):
            if set(rule_name[0]) & set(meal_rules[x][2]):
                print(meal_rules[x][2], flush=True)
                new_rules = meal_rules[x][2]
                new_rules.remove(rule_name[0][0])
                
                
                print(new_rules, flush=True)
                cursor.execute("UPDATE meals SET rules = %s WHERE user_id = %s and meals_id = %s", (new_rules, user, meal_rules[x][0]))
                connection.commit
        
        cursor.execute("DELETE FROM rules WHERE user_id = %s AND rule_id = %s", (user, rule_id,))
        connection.commit()
        no = ["Deleted the rule", "There was an error"]
        cursor.execute("SELECT * FROM rules where user_id = %s", (user,))
        rules = cursor.fetchall()
        return render_template("rules.html", no=no, rules=rules)

@app.route("/deletemeal", methods=["GET", "POST"])
@login_required
def deletemeal():
    if request.method == "POST":
        meal_id = request.form.get("meal_id")
        print(meal_id, flush=True)
        user = session.get("user_id")
        cursor.execute("DELETE FROM meals WHERE user_id = %s AND meals_id = %s", (user, meal_id,))
        connection.commit()
        no = ["Deleted the meal", "There was an error"]
        cursor.execute("SELECT * FROM meals where user_id = %s", (user,))
        meals = cursor.fetchall()
        
        return render_template("meals.html", no=no, meals=meals)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route("/login/callback")
def callback():
    # Forget any user_id
    session.clear()
    # Get authorization code Google sent back to you
    code = request.args.get("code")
    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )
    
    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Query database for username
    cursor.execute("SELECT * FROM users WHERE username = %s;", (users_email,))

    rows = cursor.fetchone()

    # Ensure username exists and password is correct
    if rows is None:
        cursor.execute("INSERT INTO users (username) VALUES(%s)", (users_email,))
        connection.commit()

    # Remember which user has logged in
    cursor.execute("SELECT * FROM users WHERE username = %s;", (users_email,))
    session["user_id"] = rows[0]

    # Redirect user to home page
    return redirect("/")


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
