from decouple import config
from flask import Flask, redirect, render_template, url_for, session

from forms import RegistrationForm
from models import db, connect_db, User, Search

app = Flask(__name__)

app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)
db.create_all()


@app.route('/', methods=['GET', 'POST'])
def signup():
    """Method used to render the home / registration
       page and create a new user in the database."""
    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        user = User.register(username, password, email)
        db.session.add(user)
        db.session.commit()
        session['username'] = username

    return render_template('register.html', form=form)