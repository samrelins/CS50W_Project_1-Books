# Books n' That

Books n' That is an implementation of a simple book reveiew website. The appliactions uses a python/flask backend and a basic HTML/jinja frontend with a bit of bootstrap CSS styling thrown in for good measure.  

The backend depends on a pre-configured postgresql database which it stays in contact with via sqlalchemy, with a schema s follows:

```
               Table "public.books"
 Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
 isbn   | text    |           | not null |
 title  | text    |           | not null |
 author | text    |           | not null |
 year   | integer |           | not null |

                Table "public.reviews"
-----------+---------+-----------+----------+--------------------------------------------
 review_id | integer |           | not null | nextval('reviews_review_id_seq'::regclass)
 user_id   | integer |           | not null |
 isbn      | text    |           | not null |
 rating    | integer |           | not null |
 review    | text    |           | not null |

                Table "public.users"
----------+--------+-----------+----------+----------------------------------------
 user_id  | bigint |           | not null | nextval('users_user_id_seq'::regclass)
 username | text   |           | not null |
 password | text   |           | not null |
 email    | text   |           | not null |
```

Note: Though sqlalchemy is a toolkit that includes extensive ORM tools, as an exercise this application is purposely executed using only raw SQL queries

The project is laid out as follows:
```
project1/
├── templates/
│   ├── layout.html
│   ├── register.html
│   ├── login.html
│   ├── logged_out.html
│   ├── index.html
│   ├── search.html
│   ├── book.html
│   └── edit_review.html
├── application.py
├── books.csv
├── import.py
├── requirements.txt
├── run_app.sh
├── static/
│   └── bootstrap-3.3.7-dist
│       ├── css 
│       ├── fonts
│       └── js
├── project1_env/
│   ├── etc....
│   ├── etc.....
│   │   ├── etc....
│   │   └── etc....
```
The following is a description of these files, in an order most appropriate to describe the logic behind the applicatoin:

# import.py / books.csv

import.py is a short python script that can be run from the command line. It takes all of the information in books.csv and inserts it entry by entry into the database's books table. The script need only be run once after the initial setup of the database and the application will then have all the information it requires to render each of the individual application pages. 

# application.py

This is the primary backend script for the application and utilises the Flask web application microframework. The script starts as you would expect by loading the required dependencies and libraries. Next, are checks to ensure the necessary environment variables are set, and then variables created to start the sqlalchemy session that allows the application to 'speak' to the database. Following this is a 'login decorator' - this is a 'shortcut' of sorts that inserts the two lines of code:
```
if session.get("user_id") is None:
    return redirect("/login")
```
at the top of any function preceeded by the decorator `@login_required`. As should hopefully be obvious from at least the choice of name, this requres that the user be logged in (or more specifically that the "user_id" variable within the users session is set) for any of the functions it preceeds. 

The remaining structure of the script is broken down into several 'routes' through which the HTML reqests are directed, facilitated by the flask `@app.route` decorator function. With the exception of the 'api' route, there is a html file corresponding to, and sharing a name with, each of the routes. Each route function dictates the information the server takes from the database and provides to the client and, in reverse, takes information sent from the client and adds it to the database. 

The HTML files all include Jinja script that is used to dictate the raw HTML that is passed to the client each time the  Flask `render_template` function is called in application.py. Flask takes the information collected from the database (and any additional varables in the script) and uses it to render the html template according to the Jinja instrucitons in the html file.  

The following is a brief description of each route and it's corresponding html file:

<h3>login</h3>

Unsurprisingly, this function allows existing users to log in. If the server receives a `POST` request at this address, it takes the information provided by the user and:
<br>

  * checks that a username/password has been submitted
  * queries the users table in the database for a matching user
  * checks the user exists, and that the password provided matches the hashed password returned from the database using Flask's `check_password_hash`
  * if any of the above fail, the server returns the login screen with an error message - the error message is rendered in the html template inside the `{% if error %}` Jinja tag
  * otherwise a Flask `session` object is created for the server to keep track of the client's activity whilst logged in
  * returns the index screen
 
Again unsurprisingly, if the user submits a `GET` request the server just returns the login screen HTML (without any error messages).

<h3>register</h3>

The register page allows users to register to use the site (shockingly) and is similar in spirit and functionality to the login page. If a `POST` request is received:
<br>

  * the information is checked for completeness 
  * password and confirmation are checked to ensure equality
  * the database is queried for a user with the same username, in the hope the submitted username is not in use
  * failure of the above returns the register page with an error - this is rendered using another Jinja `{% if error %}` tag
  * the user's password is hashed with Flask's `generate_password_hash`
  * the user's information is inserted into the users table in the database
  * the new user record is queried from the database (as a new ID is created as each user is inserted) and the user ID set in the user's `session` object
  * the server returns the index page
  
Again, a `GET` request just returns the register page HTML without any error.

<h3>logout</h3>

Logs the user out by calling the `clear` method of Flask's `session` object - functionally, this will prevent the server from recalling the user's login information should further request's come from the client device. A logut screen is then regturned to the client (actually called logged_out.html to avoid any semantic confusion).

<h3>index</h3>

This is the default page of the application. Provided the user is logged in (see the info about the `@login_required` decorator above) the server simply returns a HTML page with a form asking the user to search for a book.
