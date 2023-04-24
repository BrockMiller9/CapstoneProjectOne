from api_key import API_KEY
import requests
from flask import Flask, render_template, request,  redirect, url_for, session, flash, jsonify
import random
from forms import RegistrationForm, LoginForm
from models import db, connect_db, User, Book, Favorites
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd12345asdasd'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///book_appUI"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


connect_db(app)

db.create_all()

base_url = 'https://www.googleapis.com/books/v1/'


def get_most_popular_books(num_books=8):
    """Get the most popular books from the Google Books API"""
    query = "most popular books"
    return get_top_books(query, num_books)


def get_top_books(query, num_books=20):
    """Get the top books from the Google Books API with a given query. returns a list of books in JSON format."""
    api_key = API_KEY
    base_url = 'https://www.googleapis.com/books/v1/volumes'

    response = requests.get(base_url, params={
                            'q': query, 'maxResults': num_books, 'orderBy': 'relevance', 'key': api_key})
    results = response.json().get('items', [])

    return results


@app.route('/books_by_genre_json/<genre>')
def books_by_genre_json(genre):
    """Using this route in my javascript to get the books by genre and load them dynamically onto the webpage.  """
    books = get_top_books(f"subject:{genre}", num_books=6)
    return jsonify(books)


def get_books_of_the_year(num_books=5):
    """Get the books of the year from the Google Books API- this is being displayed on the homepage. returs a list of books in JSON format."""
    query = 'Books of the year'
    base_url = 'https://www.googleapis.com/books/v1/volumes'
    response = requests.get(base_url, params={
                            'q': query, 'maxResults': num_books, 'orderBy': 'relevance', 'key': API_KEY})
    results = response.json().get('items', [])
    return results


def get_book_by_query(query):
    """Get a book by a search query from the Google Books API. returns a book in JSON format."""
    api_key = API_KEY
    base_url = 'https://www.googleapis.com/books/v1/volumes'

    response = requests.get(base_url, params={
                            'q': query, 'maxResults': 1, 'orderBy': 'relevance', 'key': api_key})
    results = response.json().get('items', [])

    return results[0] if results else None


@app.route('/most_popular_books_json')
def most_popular_books_json():
    """Using this route in my javascript to get the most popular books and load them dynamically onto the webpage.  """
    books = get_most_popular_books()
    return jsonify(books)


@app.route('/homepage')
def homepage():
    """Display the homepage with the most popular books, books of the year, and a search bar. Also included queries for the 5 cover books on the homepage.
    Also checks if the user is logged in and passes the user object to the template."""
    book_queries = ['intitle:Lord of the flies', 'intitle:Gulag Archipelago',
                    'intitle:The Hunger Games', 'intitle:Lord of the Rings: The Return of the King Towers', 'intitle:The Hobbit']
    books = [get_book_by_query(query) for query in book_queries]
    books_of_the_year = get_books_of_the_year()
    most_popular_books = get_most_popular_books()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])

    return render_template('index.html', books=books, books_of_the_year=books_of_the_year, most_popular_books=most_popular_books, user=user)


@app.route('/')
def home():
    return redirect('/homepage')


@app.route('/random_book')
def random_book():
    """Get a random book from the Google Books API and display it on the page.Using multiple queries to and then randomly selecting one of them.
      Also checks if the user is logged in and passes the user object to the template."""
    queries = ['subject:fiction', 'subject:history', 'subject:travel', 'subject:science', 'subject:computers',
               'subject:philosophy', 'subject:math', 'subject:poetry', 'subject:art', 'subject:biography']
    query = random.choice(queries)
    books = get_top_books(query)
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    if books:
        book = random.choice(books)
        return render_template('book_details.html', book=book, user=user)

    else:
        return 'No books found for the query: ' + query


@app.route('/book_details/<book_id>')
def book_details(book_id):
    """Get the details of a book from the Google Books API and display it on the page. Using the book id to get the book details from the API.
      Also checks if the user is logged in and passes the user object to the template."""
    response = requests.get(base_url + 'volumes/' +
                            book_id + '?key=' + API_KEY)
    book = response.json()
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('book_details.html', book=book, user=user)


# route to display the search form
@app.route('/search_results')
def search_results():
    """Get the search results from the Google Books API and display them on the page. passing the user's query to the API.
    Using the query to get the search results from the API. Also checks if the user is logged in and passes the user object to the template."""
    query = request.args.get('query')
    response = requests.get(base_url + 'volumes?q=' +
                            query + '&key=' + API_KEY)
    data = response.json()
    books_of_the_year = get_books_of_the_year()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('search_results.html', data=data, books_of_the_year=books_of_the_year, user=user)


# route to display the sign up form
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Display the sign up form and register the user. Using the RegistrationForm to validate the form data. 
    We then save the user's email address to the database. We use Bcrypt to hash the user's password. Once the user is registered, log the user in and redirect to the homepage.
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        # registering the user
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.register(username, password)
        # add the user to the database
        user.email = email  # this is not in the register method
        db.session.add(user)
        db.session.commit()
        # log the user in
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('homepage'))

    return render_template('signup.html', form=form)


# route to display the login form
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Display the login form and log the user in. Using the LoginForm to validate the form data. """
    form = LoginForm()
    if form.validate_on_submit():
        # log the user in
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('homepage'))
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)


# route to log the user out
@app.route('/logout')
def logout():
    """Log the user out and redirect to the homepage. Clear the session and flash a message."""
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('homepage'))


@app.route('/user/<int:user_id>')
def user_detail(user_id):
    """Display the user's profile page. Get the user's details from the database and pass them to the template."""

    user = User.query.get_or_404(user_id)
    if user:
        return render_template('user_detail.html', user=user)
    else:
        flash('User not found', 'danger')
        return redirect(url_for('home'))


# route to add a book to the user's favorites
@app.route('/favorite/<book_id>', methods=['POST'])
def add_favorite(book_id):
    """Add a book to the user's favorites. Check if the user is logged in. Check if the book is already in the user's favorites."""
    # Check if the user is logged in
    if 'user_id' not in session:
        flash('You need to log in to favorite a book', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']

    # Check if the book is already in the user's favorites
    existing_favorite = Favorites.query.filter_by(
        user_id=user_id, book_id=book_id).first()
    if existing_favorite:
        flash('You have already favorited this book', 'warning')
        return redirect(url_for('book_details', book_id=book_id))

    # fetch the book title from the Google Books API
    response = requests.get(base_url + 'volumes/' +
                            book_id + '?key=' + API_KEY)
    book_data = response.json()

    book_title = book_data['volumeInfo']['title']
    # add the book to the user's favorites
    Favorites.add_favorite(user_id, book_title, book_id)

    return redirect(url_for('show_favorites'))


# route to remove a book from the user's favorites
@app.route('/unfavorite/<book_id>', methods=['POST'])
def remove_favorite(book_id):
    """Remove a book from the user's favorites. Check if the user is logged in."""
    if 'user_id' not in session:
        flash('You need to log in to unfavorite a book', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    Favorites.remove_favorite(user_id, book_id)
    return redirect(url_for('show_favorites'))


# route to display the user's favorites
@app.route('/favorites')
def show_favorites():
    """Display the user's favorites. Check if the user is logged in. Get the user's favorites from the database and pass them to the template."""
    if 'user_id' not in session:
        flash('Please log in to view your favorite books', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = User.query.get_or_404(user_id)
    books_of_the_year = get_books_of_the_year()
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    return render_template('favorites.html', favorites=favorites, books_of_the_year=books_of_the_year, user=user)


if __name__ == '__main__':
    app.run(debug=True)
