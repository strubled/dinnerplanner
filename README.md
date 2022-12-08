# dinnerplanner

### A simple app that helps you plan out what to eat for dinner

## Why did I build this

The main reason is I needed something to build as my final project for CS50x. I thought for a while what sort of problem should I try to solve, and inspiration struck right around dinner time.  

How many people out there ask themselves every day - what's for dinner?  It's really hard to figure this out, but it shouldn't be.  My idea was to let someone tell a system about their meals and the rules they apply to those meals.  For example, let's say you sometimes want to avoid eating meat or cheese.  With this app, you'd be able to tell the system "get me a random meal that doesn't have cheese or meat".  

## Where to take this in the future

I really want to build a 7 day view based on additional rules.  For example, let's say you eat pizza every friday, you only want to eat meat one time per week, and you don't want to eat foods with red sauce two days in a row.  After you enter in all of your meals, you should be able to just press a button to get a week's worth of meals.  

## How I built this

1. Utilized python, flask, html and css (mainly generic boostrap with a few small tweaks).  
2. For my database, used PostgreSQL. Lessons learned for this is I am using psycopg2 which apparently is an older style vs. using SQLAlchemy.  I also took a short cut and am not utilizing code to create the tables / run migrations.  There are only three tables, so I just created them manually (you can see the commands for that further down)
3. For user login / pw reset...I started down a path of rolling my own, but after futzing around with JWT tokens for a few days, I abandoned ship and am using Google login instead.  It was neat to learn how this worked and made things super simple!
4. I deployed originally to Heroku...this was fairly straightforward once I figured out that I needed to start the Dyno.  The downside of this is Heroku is no longer free, and I'm cheap, so I took the site down a day after I launched it lol.  Someday I may spend some time investigating a cheaper option.

## How to get it running

1. Set up a Postgres database, and create three tables:

- CREATE TABLE users (user_id serial PRIMARY KEY, username CHAR (50) NOT NULL);
- CREATE TABLE meals(meals_id serial PRIMARY KEY, mealname VARCHAR ( 50 ) NOT NULL, rules text ARRAY, user_id serial NOT NULL);
- CREATE TABLE rules(rule_id serial PRIMARY KEY, rule_name VARCHAR ( 50 ) UNIQUE NOT NULL, value boolean NOT NULL);

2. Update the connection details (you'll want to store them in os.variables when you go to prod)
3. Go to Google and set up oauth creds (for the sign in).  This part is tricky.  This doc helped me a ton: https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwiOsrH3hen7AhXKFlkFHfRODIIQFnoECA0QAQ&url=https%3A%2F%2Frealpython.com%2Fflask-google-login%2F&usg=AOvVaw1EHaaCXg9bg0iI29czVPXz

- when testing in dev, Google needs SSL.  To fake this out, run your app with FLASK_APP="app:app" flask run --cert=adhoc


