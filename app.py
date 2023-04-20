from api_key import API_KEY
import requests
from flask import Flask, render_template, request,  redirect, url_for, session, flash
import random
from forms import RegistrationForm, LoginForm
from models import db, connect_db, User, Book, Favorites
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcd12345asdasd'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///book_app"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True


connect_db(app)

db.create_all()


base_url = 'https://www.googleapis.com/books/v1/'

# make a route that queries the Google Books API for a book entered by the user into the url


@app.route('/test')
def test():
    return render_template('test.html')


def get_top_books(query, num_books=20):
    api_key = API_KEY
    base_url = 'https://www.googleapis.com/books/v1/volumes'

    response = requests.get(base_url, params={
                            'q': query, 'maxResults': num_books, 'orderBy': 'relevance', 'key': api_key})
    results = response.json().get('items', [])

    return results


@app.route('/')
def home():
    query = 'best sellers'
    books = get_top_books(query)
    if books:
        return render_template('top_books.html', books=books)

    else:
        return 'No books found for the query: ' + query

# create a route that display the details of one random book


@app.route('/random_book')
def random_book():
    queries = ['subject:fiction', 'subject:history', 'subject:travel', 'subject:science', 'subject:computers',
               'subject:philosophy', 'subject:math', 'subject:poetry', 'subject:art', 'subject:biography']
    query = random.choice(queries)
    books = get_top_books(query)
    if books:
        book = random.choice(books)
        return render_template('book_details.html', book=book)

    else:
        return 'No books found for the query: ' + query


@app.route('/book_details/<book_id>')
def book_details(book_id):
    response = requests.get(base_url + 'volumes/' +
                            book_id + '?key=' + API_KEY)
    book = response.json()
    return render_template('book_details.html', book=book)

# route to display the search form


@app.route('/search_results')
def search_results():
    query = request.args.get('query')
    response = requests.get(base_url + 'volumes?q=' +
                            query + '&key=' + API_KEY)
    data = response.json()
    return render_template('search_results.html', data=data)

# route to display the sign up form


@app.route('/signup', methods=['GET', 'POST'])
def signup():
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
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)

# route to display the login form


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # log the user in
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html', form=form)

# route to log the user out


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))


# route to display the user info page


@app.route('/user/<int:user_id>')
def user_detail(user_id):

    user = User.query.get_or_404(user_id)
    if user:
        return render_template('user_detail.html', user=user)
    else:
        flash('User not found', 'danger')
        return redirect(url_for('home'))


# route to add a book to the user's favorites
@app.route('/favorite/<book_id>', methods=['POST'])
def add_favorite(book_id):
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
    if 'user_id' not in session:
        flash('You need to log in to unfavorite a book', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    Favorites.remove_favorite(user_id, book_id)
    return redirect(url_for('show_favorites'))


# route to display the user's favorites
@app.route('/favorites')
def show_favorites():
    if 'user_id' not in session:
        flash('Please log in to view your favorite books', 'danger')
        return redirect(url_for('login'))
    user_id = session['user_id']
    favorites = Favorites.query.filter_by(user_id=user_id).all()
    return render_template('favorites.html', favorites=favorites)


if __name__ == '__main__':
    app.run(debug=True)
