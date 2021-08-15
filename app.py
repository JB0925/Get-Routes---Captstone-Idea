from datetime import time
import json

from decouple import config
from flask import Flask, redirect, render_template, url_for, session, request

from forms import RegistrationForm, LoginForm, RouteSearchForm
from models import db, connect_db, User, Search
from get_routes import get_route_data, create_search_string

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
    form = RouteSearchForm()

    if form.validate_on_submit():
        length = 0
        street_address = form.street_address.data
        city = form.city.data
        state = form.state.data
        full_address = create_search_string(city, state, street_address)
        route_data = get_route_data(full_address)
        
        if route_data:
            user = User.query.filter_by(username=session["username"]).first()
            for key in route_data:
                length += 1
                new_route = Search(time=route_data[key][0], transportation_mode=route_data[key][1],
                                        destination=route_data[key][2], website=route_data[key][3], user_id=user.id)
                db.session.add(new_route)
                db.session.commit()
            return redirect(url_for('show_results', length=length))
        return redirect(url_for('not_found'))
    
    if "username" in session:
        return render_template('search.html', form=form)
    return redirect(url_for('login'))


@app.route('/search/results')
def show_results():
    user = User.query.filter_by(username=session['username']).first()
    print(user.searches)
    length = request.args.get('length')
    if not length:
        return redirect(url_for('search_routes'))
    length = int(length)
    routes = Search.query.all()[-length:]
    return render_template('results.html', routes=routes)


@app.route('/404')
def not_found():
    return render_template('404.html')


@app.route('/logout')
def logout():
    if "username" in session:
        session.pop("username")
    return redirect(url_for('login'))