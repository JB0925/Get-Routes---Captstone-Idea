from unittest import TestCase

from flask_bcrypt import Bcrypt
from flask import session, render_template, Flask
from decouple import config

from app import app, MAP_ARRAY
from models import db, User, Search
from forms import RegistrationForm


bcrypt = Bcrypt()

app.config['SQLALCHEMY_DATABASE_URI'] = config('TEST_DB')

db.drop_all()
db.create_all()


def create_app(cfg=None):
    app = Flask(__name__)
    return app

class RideFinderTestCase(TestCase):
    def setUp(self) -> None:
        app.config["TESTING"] = True
        app.config['WTF_CSRF_ENABLED'] = False
        User.query.delete()
        Search.query.delete()
    

    def tearDown(self) -> None:
        db.session.rollback()
    

    def mock_station(self):
        return {
            0: ['Culpeper Amtrak', 38.4722, -77.9935]
        }
    
    def mock_directions(self):
        return [
            ["Turn right on Davis St."]
        ]
    

    def mock_route_information(self):
        return {
            0: [
                '2021-08-22 @ 19:52PM',
                'regionalTrain',
                'Crescent',
                'Chicago Union Station',
                'Chicago Union Station',
                'https://www.amtrak.com'
            ]
        }
    

    def remove_from_db(self, db_item):
        db.session.delete(db_item)
        db.session.commit()
    

    def make_user(self):
        password = bcrypt.generate_password_hash('cookies').decode('utf-8')
        user = User(username='kim08', password=password, email='kim08@gmail.com')
        db.session.add(user)
        db.session.commit()
        return user
    

    def login_user(self, user):
        with app.test_client() as client:
            return client.post('/login', data={"username": user.username, "password": "cookies"},
                                    follow_redirects=True)
    

    def logout_user(self, user):
        with app.test_client() as client:
            return client.get('/logout')
    

    def test_about_route(self):
        """
        Test to make sure the 'About' route is rendering correctly.
        """
        with app.test_client() as client:
            resp = client.get('/about')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Springboard', resp.get_data(as_text=True))
    

    def test_404_route(self):
        """
        Test to make sure the '404' route is rendering correctly.
        """
        with app.test_client() as client:
            resp = client.get('/404')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sorry!', resp.get_data(as_text=True))
    

    def test_login_route(self):
        """
        Testing a POST request, a GET request, and a GET request with an
        already logged in user.
        """
        with app.test_client() as client:
            resp = client.post('/login', data={"username": "kim08", "password": "cookies"})
            self.assertEqual(resp.status_code, 302)

            resp2 = client.get('/login')
            self.assertEqual(resp2.status_code, 200)
            self.assertIn('Sign', resp2.get_data(as_text=True))

            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            resp3 = client.get('/login')
            self.assertEqual(resp3.status_code, 302)
    

    def test_register_route(self):
        """
        Testing a POST request, a GET request, and a GET request with an
        already logged in user.
        """
        with app.test_client() as client:
            resp2 = client.get('/')
            self.assertEqual(resp2.status_code, 200)
            self.assertIn('Welcome', resp2.get_data(as_text=True))

            with client.session_transaction() as sesh:
                sesh["username"] = "kim08"
            
            resp3 = client.get('/')
            self.assertEqual(resp3.status_code, 302)
    

    def test_register_route_post(self):
        with app.test_client() as client:
            resp = client.post('/', data=dict(username="kim08", password="cookies", email="kim@gmail.com"), follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            # self.assertEqual(len(User.query.all()), 1)
    

    def test_logout_route(self):
        """
        Testing to sure the logout view actually logs a user out.
        """
        with app.test_client() as client:
            user = self.make_user()
            self.login_user(user)
            self.logout_user(user)
            resp = client.get('/logout')
            self.assertEqual(resp.status_code, 302)


    def test_render_stations_template(self):
        app2 = create_app()
        stations = self.mock_station()
        directions = self.mock_directions()
        @app2.route('/search/results')
        def show_stations():
            return render_template('station_results.html', routes=stations, directions=directions, maps=MAP_ARRAY)
        with app2.test_client() as client:
            resp = client.get('/search/results')
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Culpeper", resp.get_data(as_text=True))
            self.assertIn("Turn", resp.get_data(as_text=True))
    

    def test_show_routes(self):
        """
        This test serves to assert that the route responds as expected, 
        and that the template also responds to the data being passed to it.
        """
        # Test the template itself through a dummy app
        app2 = create_app()
        route_information = self.mock_route_information()
        names = ['Chicago Union Station']

        @app2.route('/stations/0/routes')
        def show_routes():
            return render_template('route_results.html', routes=route_information, maps=MAP_ARRAY, names=names)

        with app2.test_client() as client:
            resp = client.get('/stations/0/routes')
            self.assertIn('Chicago', resp.get_data(as_text=True))
        
        # Test the app view itself, irrespective of the template
        with app.test_client() as client:
            resp2 = client.get('/stations/9/routes', follow_redirects=True)
            self.assertEqual(resp2.status_code, 200)
            self.assertIn("Login", resp2.get_data(as_text=True))
    

    def test_check_email_exists_route(self):
        """Test to check that the 'Reset Password' page works and asks for an email address."""
        with app.test_client() as client:
            resp = client.get('/reset/email')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Please enter the email address associated with your account.',
                            resp.get_data(as_text=True))
    

    def test_enter_new_password_route(self):
        with app.test_client() as client:
            resp = client.get('/reset')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Reset your password.', resp.get_data(as_text=True))


