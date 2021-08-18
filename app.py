from decouple import config
from flask import Flask, json, redirect, render_template, url_for, session, request, jsonify

from forms import RegistrationForm, LoginForm, RouteSearchForm
from models import db, connect_db, User, Search
from get_routes import get_lat_and_long, get_route_data, create_search_string, get_station_data, _get_routes_and_stations

app = Flask(__name__)

app.config['SECRET_KEY'] = config('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = config("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

connect_db(app)
db.create_all()

# global variables used to send data on client-side requests
coords = []
destination_coords = []
lat_and_lng = {}
stations = {}
city_and_state = {'address': None}
MAP_ARRAY = ['map', 'hybrid', 'satellite', 'dark', 'light']
LIMIT = -5

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
        return redirect(url_for('search_stations'))

    if "username" in session:
        return redirect(url_for('search_stations'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Method used to render the login page and login
       an existing user."""
    form = LoginForm()

    if request.method == 'GET':
        if "username" not in session:
            return render_template('login.html', form=form)
        return redirect(url_for('search_stations'))
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            session['username'] = username
            return redirect(url_for('search_stations'))
    return redirect(url_for('signup'))


@app.route('/search', methods=['GET', 'POST'])
def search_stations():
    """Method used to locate public transit stations within a 
       500 meter radius of the address given by the user."""
    global stations
    global coords
    global lat_and_lng
    global city_and_state
    form = RouteSearchForm()

    if form.validate_on_submit():
        street_address = form.street_address.data
        city = form.city.data
        state = form.state.data
        full_address = create_search_string(city, state, street_address)
        coords = get_route_data(full_address)
        city_and_state['address'] = f'{city}, {state.upper()}'
        try:
            lat, lng = get_lat_and_long(full_address)
        except TypeError:
            return redirect(url_for('search_stations'))
        lat_and_lng["latitude"] = lat
        lat_and_lng["longitude"] = lng

        # gets data about stations and then packages it into an easier to read format
        station_data = _get_routes_and_stations(lat,lng)
        stations = get_station_data(station_data)
        
        if station_data:
            return redirect(url_for('show_station_results'))
        return redirect(url_for('not_found'))
    
    # handles any GET requests based on whether the user is logged in or not
    if "username" in session:
        return render_template('search.html', form=form)
    return redirect(url_for('login'))


@app.route('/search/results')
def show_station_results():
    """Renders the page to show transit stations located near
       the address the user gave. Passes the global stations
       variable to the template, as well as an array used to
       give each map an id (used in rendering the maps)."""
    global stations
    return render_template('station_results.html', routes=stations, maps=MAP_ARRAY)


@app.route('/stations/<idx>/routes')
def show_route_results(idx):
    """Shows a list of all routes and their relevant information,
       as well as setting data to be used in a client-side call
       that is used to render the maps."""
    global coords
    idx = int(idx)

    # handling GET requests and edge cases.
    if "username" not in session:
        return redirect(url_for('signup'))
    if idx < 0 or idx > 4:
        return redirect(url_for('search_stations'))
    if not coords:
        return redirect(url_for('search_stations'))
    
    routes = coords[idx]
    names = []
    user = User.query.filter_by(username=session["username"]).first()
    for key in routes:
        names.append(key[2])
        destination_coords.append(get_lat_and_long(f'{key[2]} {city_and_state["address"]}'))
        new_route = Search(time=key[0], transportation_mode=key[1],
                                destination=key[4], website=key[5], user_id=user.id)
        db.session.add(new_route)
        db.session.commit()
    
    available_routes = Search.query.all()[LIMIT:]
    return render_template('route_results.html',routes=available_routes, maps=MAP_ARRAY, names=names)


@app.route('/get_coords')
def get_coords():
    """A route used by the client-side to get data
       about the stations that will allow maps to 
       be rendered."""
    return jsonify(stations)


@app.route('/get_routes')
def get_routes():
    """A route used by the client-side to get data
       about the routes for a selected station. It
       also gives the client-side the data that allows
       the maps to be rendered."""
    global lat_and_lng
    global city_and_state
    global destination_coords
    routes = [r.serialize for r in Search.query.all()[-5:]]

    routes.append(lat_and_lng)
    routes.append(city_and_state)
    routes.append(destination_coords)
    destination_coords = []
    return jsonify(routes)


@app.route('/404')
def not_found():
    """A page used when a user types in information
    for which there is no match."""
    return render_template('404.html')


@app.route('/logout')
def logout():
    """Handles logging out a user."""
    if "username" in session:
        session.pop("username")
    return redirect(url_for('login'))