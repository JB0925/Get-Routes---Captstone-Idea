from decouple import config
from flask import Flask, redirect, render_template, url_for, session, request

from forms import RegistrationForm, LoginForm
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


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Method used to render the login page and login
       an existing user."""
    form = LoginForm()

    if request.method == 'GET':
        if "username" not in session:
            return render_template('login.html', form=form)
        return redirect(url_for('search_routes'))
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('search_routes'))
    return redirect(url_for('signup'))


@app.route('/search', methods=['GET', 'POST'])
def search_routes():
    return render_template('search.html')