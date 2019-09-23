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

<h2>import.py / books.csv</h2>

import.py is a short python script that can be run from the command line. It takes all of the information in books.csv and inserts it entry by entry into the database's books table. The script need only be run once after the initial setup of the database and the application will then have all the information it requires to render each of the individual application pages. 

<h2>application.py & HTML templates</h2>

`applicatin.py` forms the primary python instructions for the application and utilises the Flask web application microframework. 

The script starts as you would expect by loading the required dependencies and libraries. Next, are checks to ensure the necessary environment variables are set, and then variables created to start the sqlalchemy session that allows the application to 'speak' to the database. Following this is a 'login decorator' - this is a 'shortcut' of sorts that inserts the two lines of code:
```
if session.get("user_id") is None:
    return redirect("/login")
```
at the top of any function preceeded by the decorator `@login_required`. As should hopefully be obvious from at least the choice of name, this requres that the user be logged in (or more specifically that the "user_id" variable within the users session is set) for any of the functions it preceeds. 

The remaining structure of the script is broken down into several 'routes' through which the HTML reqests are directed, facilitated by the flask `@app.route` decorator function. With the exception of the 'api' route, there is a html file corresponding to, and sharing a name with, each of the routes. Each route function dictates the information the server takes from the database and provides to the client and, in the reverse direction, the information taken from the client and inserted into the database. 

The HTML files all include Jinja script that is used to help customise the raw HTML that is passed to the client each time the Flask `render_template` function is called in application.py. Flask uses the instructions provided by the Jinja script in the HTML templates to render variable information in the HTML templates, such as the information provided by the routes in `application.py`. The result is that the need for thousands of individual raw HTML files, and the need to copy lots of identical HTML, is a avoided by allowing more variability in each of the HTML templates.

<h3>layout.html</h3>

A good example of this is the `layout.html` template, which comprises the header information to be included on each of the other HTML templates on the site. This information would otherwise need to be laboriously copy/pased onto each template and, if changed, laboriously copy/pasted over again. The Jinja script avoids this by the various `{% block \[variable\] %}{% endblock %}` tags, that instruct flask to insert "chunks" of HTML from the other template files into the corresponding space occupied by these tags.

The following is a brief description of each route and it's corresponding html template:

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

<h3>search</h3>

Once a user submits an search it is routed as a `POST` request through the `search` route. 

The function executes a SQL `LIKE()` query with the submitted search string to each of the `author` / `title` / `ISBN` features of the `books` table. The `LIKE()` operator is used in a similar vain to python's regular expressions, i.e. you submit a query using wildcard charachters to specify custom search perameters. This particular example is a really simple use of the `%` wildcard charachter at either end of the search string - this is a placeholder of zero or more charachters, allowing users to search for example "Harry Potter and the Philosopher's Stone" by simply typing "Potter". 

SQL lite then returns a list of up to 30 books matching the user's query, that is then passed to the `render` function along with the `search.html` template. The script in the `search.html` checks that the search returned any results using a simple Jinja `{% if books %}` operator: if so it creates a table and loops over the entries in books using `{% for book in books %}` to fill the entries in the table, if not just renders a script advising the user their search yielded no results.

<h3>book</h3>

The `book` route is responsible for rendering book & user information when receiving a `GET` request, and inserting new reviews into the `reviews` table when a user submits a book review. The function is called with an `isbn` variable that is included as a "variable section" of the route's url; this is a common feature of flask applications - the `<string:isbn>` that follows `book/` in the URL of the `@app.route` decorator function effectively creates an individual URL for each isbn in the `books` table. The function then executes the following instructions:

  * takes any information provided by the client if a `POST` request is submitted, checks for completeness, and inserts complete info into the `reviews` table or updates the `error` variable for incomplete submissions
  * queries the `books` table for the relevant book's information
  * submits a request to the goodreads API and extracts the `average_rating` and `work_ratings_count` features
  * queries the `reviews` table for reviews by the current user / other users and the average overall rating from all users
  * passes all this information to the `render_template` function, that render's the `book.html` template
  
The `book.html` template includes the following features:
<br>
  * The template checks if the user has already submitted a reveiw with `{% if user_review %}` - if so, the user's review is displayed with the option to edit it. Otherwise a form is displayed inviting the user to leave a review (and `{% if error %}` displays an error message if the user attempted to submit an incomplete review)
  * If other users have submitted reviews, the `{% for review in other_reviews %}` statement separates out each individual `reveiw` entry and displays its information. 
  
<h3>edit_review</h3>
