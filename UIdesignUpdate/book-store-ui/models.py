from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from api_key import API_KEY
import requests
from sqlalchemy.orm.exc import NoResultFound


db = SQLAlchemy()

bcrypt = Bcrypt()
base_url = 'https://www.googleapis.com/books/v1/'


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """Site user."""

    __tablename__ = "users"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    username = db.Column(db.Text,
                         nullable=False,
                         unique=True)

    password = db.Column(db.Text,
                         nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)

    # start_register

    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)
    # end_register

    # start_authenticate
    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False
    # end_authenticate


class Favorites(db.Model):
    """Favorites."""

    __tablename__ = "favorites"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    book_title = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Text, db.ForeignKey(
        'books.book_id'), nullable=False)

    user = db.relationship('User', backref='favorites')
    book = db.relationship('Book', backref='favorites')

    # function to add a favorite to the database
    @classmethod
    def add_favorite(cls, user_id, book_title, book_id):
        book = Book.query.filter_by(book_id=book_id).one_or_none()
        if not book:
            response = requests.get(
                base_url + 'volumes/' + book_id + '?key=' + API_KEY)
            book = response.json()
            book = Book(title=book['volumeInfo']['title'], author=book['volumeInfo']['authors'][0], description=book['volumeInfo']
                        ['description'], image=book['volumeInfo']['imageLinks']['thumbnail'], book_id=book_id)
            db.session.add(book)
            db.session.commit()

        favorite = cls(user_id=user_id, book_id=book_id, book_title=book_title)
        db.session.add(favorite)
        db.session.commit()

    # function to remove a favorite from the database
    @classmethod
    def remove_favorite(cls, user_id, book_id):
        favorite = Favorites.query.filter_by(
            user_id=user_id, book_id=book_id).first()
        db.session.delete(favorite)
        db.session.commit()


class Book(db.Model):
    """Book."""

    __tablename__ = "books"

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)

    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    book_id = db.Column(db.Text, nullable=False, unique=True)

    user = db.relationship('User', secondary='favorites', backref='books')
