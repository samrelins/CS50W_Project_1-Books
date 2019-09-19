# Books & Stuff

Books and stuff is a thrilling book review website. You can create an account an leave a reviews for any of 5000 books stored in the sites bowels. "Bowels" refers more specifically to the site's postgresql database which contains tables for each of the aforementioned books, the site's users and the reveiws left by said users for said books. Simple.

The schema (or organisation) of the database looks like this:
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

The database is hosted on heroku.com. Nice place. Highly reccomended. 

The site itself is comprised of a python-based server with all the fancy stuff handled by a python micro-framework called flask. The rest is then handled by various HTML pages with the odd bit of jinja that talks to the flask/python app. The site is styled using some lovely bootstrap components and overall styling. 

The project is laid out as follows:
```
project1/
├── application.py
├── import.py
├── books.csv
├── requirements.txt
├── run_app.sh
├── templates/
│   ├── layout.html
│   ├── register.html
│   ├── login.html
│   ├── logged_out.html
│   ├── index.html
│   ├── search.html
│   ├── book.html
│   └── edit_review.html
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
the following are quick individual rundowns of each of the above files/directories/bags of fun:

# application.py

The workhorse of the site, this is the python application that does all of the legwork behind the scenes to talk to the browser making requests and the database that stores all the deets. The app is broken down into several routes that each speaks to one (or more) of the HTML templates stored in the templates folder. For simplicity and structure an expanation of each route will be given as part of the discussion of each respective html template.

The file starts by importing all of the required libraries and functions that are used in the application followed by a couple of statements configuring the database and app. Then follows a "decorated function" for those app routes requiring a login - this is basically a fancy way of saving the need to have the same 3 lines of code at the beggining of the routes that require a user to be logged in. All of the application routes then follow.

# import.py / books.csv

This is a very short and simple application that uses sqlalchemy (flasks library that speaks to your database for you) to take the data from books.csv and upload it to the postgresql database in the format above. 

# requirements.txt

This is a simple list of the various flask modules required for the app to work. Nothing particularly spectacular here, but this will be discussed in greater detail when talking about project1_env.

# run_app.sh

This is a simple bash script that automatically sets the API and DATABASE_URL environment variables, activates the virtual environment in which the application runs and then runs the flask app. Basically, its a pain to keep having to perform each of these steps one by one before launching the server. 

Interesting aside: don't assume that running such a script is identical to inputting a command in the terminal - it works more like a running a program that exits once it reaches the end of the script. In other words, putting the line "export API_KEY=......" in a shell script then running it will simply set that environment variable for a split second while the script runs. It wont be retained once the script is exited. As such, the run_app.sh script works because it sets each of the environment variables and then runs flask straight away.

# Templates

Each template includes the html script that lays out the pages of the web application (with a bit of help from the css and js discussed later) and talks to one or more of the @routes in application.py 

# layout.html

This is the basic skeleton of each of the pages of the application. It includes all of the basic structure that it would be a pain to have to keep repeating e.g. the metadata in the page head with the styling and the navbar at the top of each page. This file also nicely demonstrates jinja syntax in action. Tags are used to extend these elements of the template to create the individual pages of the site. These tags correspond with those on the other html pages to "plug in" the different sections of the site required to render the whole page.

# register.html

Unsurprisingly, this page allows a user to register with the site. The html is just a basic form that asks for the info required for registration and is served up when the user reaches this route via a GET request. The form then submits the info to the @register route as a POST request once completed, and the app adds the details to the database checking for any errors en-route. If any errors are detected, the register page is re-rendered with an error message saying what went wrong. Otherwise, the users details are added to the database, stored as a session and the user is directed to the index page.

# login.html

Again, pretty obvious this one. The html displays a form asking for a username and password. This is taken from the form via a POST request to @login which checks the details agians the info in the database. If the details are correct, the users info is stored in the session and they are redirected to the login page. Otherwise the login screen is re-rendered and an error message displayed explaining the problem.

# logged_out.html

So obvious it hurts.

# index.html

The index page is the default (or "/") route. It's another basic form that asks the user for a search term. The search term is then passed to the app as a POST request to the @search route. 

# search.html

The search page is used to render the results of a book search. The search itself queries the database for any entries that have a similar author, title or ISBN to the users search. It then returns table data to the search page, which uses some jinja wizardry to render the results in a table using a for loop. Users can then select one of the entries in the table to be linked to the page for that individual book. If the search doesn't return any results, a jinja if / else statement checks for this and informs the user. 

# book.html

This is the meat of the site. The book page takes the isbn details of the book (stored in the url for the individual book page) and the application queries the database for the details of the book. It then renders the info for the book at the top of the screen. Alonside the details from the site's database, is info from the goodreads API showing the number of reviews and the average rating from the goodreads site. 

Below this is the reviews section. If the user has already submitted a review, this is displayed at the top of this section along with the option to edit their submission. Otherwise a form is displayed asking for a text review and a rating out of 5. On submission this info is sent via the @review route which includes an ISBN reference using the format /review/"isbn". The application then takes the review via the @review route and adds it to the database and refreshes the book page. Now the user has submitted a review it is displayed at the top of the page.

Below the user's review (or lack thereof) are any reviews submitted by other users and an average score. The data for the user reviews is fed into the page from the info in the database via the app's @book route and is formatted using some clever jinja. Note that the reviews are either displayed one on top of the other or in rows of three depending on what size device is being used. 

# edit_review.html

The edit review page is formatted identacally to the book page with the form submission present - just minus the other user reviews at the bottom and with an additional line at the top of the form showing the existing review to be edited. The user can then submit a replacement review in much the same way as they did the original. 

Submissions are sent from the page to the @edit_review route. This checks for errors as usual and then updates the user's review entry in the database, returning the user to the relevant book page once complete. 

# static

One of the features of flask is that it looks for different parts of your web application in pretty specific places. Specifically, you need to tell flask exactly what the name of your pythong application file is (hence the FLASK_APP variable in the run_app.sh script), all of the html templates for your site need to be stored in a folder called "templates" and any css or javascript files need to go in a folder called static.

To make life easy this site uses bootstrap for all its styling and whatnot and so the standard boostrap distribution files are found in the static folder for this app.

# project1_env

One of the 'quirks' of using python and flask to create web apps is that, often, a large number of additional add-on's or plugins are required to make things tick. When using python and flask in several different applications these can start to conflict with eachother and even the system itself causing untold frustration. 

An easy way to overcome this issue is to create an environment in which your application opperates. This effectively 'isolates' your applicaton in its own little bubble - any plugins or additonal python modules you install will be kept separate from your underlying system and will only affect the running of your python program when inside that specific environment. The environment is activated as part of the run_app.sh script before flask is run, ensuring that all the gubbins specific to project1 are present as the server is initiated. Magic.
