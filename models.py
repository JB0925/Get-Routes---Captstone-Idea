from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Method used to connect database upon
       app startup."""
    db.app = app
    db.init_app(app)


class User(db.Model):
    """Model class used to store information about
       users who register to use the app."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, unique=True)

    searches = db.relationship('Search', backref='user')


    @classmethod
    def register(cls, username: str, password: str, email: str):
        """This method hashes a user's password and creates a User 
           instance, which can then be saved to the database."""
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        return cls(username=username, password=hashed_pw, email=email)
    

    @classmethod
    def authenticate(cls, username, password):
        """This method is used to sign a user in by 1).
           checking to see that the username exists in the database
           and 2). ensuring that the given password matches the hash
           of the stored password."""
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        return False


class Search(db.Model):
    """Model that saves information from previous searches that users made."""
    __tablename__ = 'searches'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String)
    transportation_mode = db.Column(db.String)
    destination = db.Column(db.String)
    website = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)
