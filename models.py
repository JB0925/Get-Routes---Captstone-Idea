from os import name
from flask_sqlalchemy import SQLAlchemy # type: ignore
from flask_bcrypt import Bcrypt # type: ignore
from sqlalchemy.orm import backref # type: ignore


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
    email = db.Column(db.String, unique=True, nullable=False)

    searches = db.relationship('Search', backref='user')
    origins = db.relationship('OriginInfo', backref='user')
    stations = db.relationship('Station', backref='user')
    directions = db.relationship('StationDirection', backref='user')
    routes = db.relationship('RouteData', backref='user')


    def __str__(self):
        return f'User(username={self.username}, password={self.password}, email={self.email}'


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


    @property
    def serialize(self):
        """Method used to serialize a Search object so that 
        it can be returned as JSON data to the client-side."""
        return {
            "time": self.time,
            "mode": self.transportation_mode,
            "destination": self.destination,
            "website": self.website,
        }


class OriginInfo(db.Model):
    """Table used to gather the data from the search string the user inputs."""
    __tablename__ = 'origins'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city_and_state = db.Column(db.String, nullable=False)
    latitude = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    
    @property
    def serialize(self):
        return {
            "address": self.city_and_state,
            "latitude": float(self.latitude),
            "longitude": float(self.longitude)
        }


class Station(db.Model):
    """Table used to gather the data for each station returned by the API."""
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    station_latitude = db.Column(db.String, nullable=False)
    station_longitude = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "station_latitude": float(self.station_latitude),
            "station_longitude": float(self.station_longitude)
        }
    

    @classmethod
    def batch_commit(cls, data, id):
        for d in data:
            station = cls(name=data[d][0], station_latitude=str(data[d][1]), station_longitude=str(data[d][2]), user_id=id)
            db.session.add(station)
        db.session.commit()


class StationDirection(db.Model):
    """Table used to save all of the directions to the station"""
    __tablename__ = 'station_directions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    directions = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    
    @classmethod
    def batch_commit(cls, data, id):
        for group in data:
            temp = ''
            for direction in group:
                temp += f'{direction}+'
            directions = cls(directions=temp, user_id=id)
            db.session.add(directions)
        db.session.commit()


class RouteData(db.Model):
    """Table used to save all data for each route."""
    __tablename__ = 'route_data'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    mode = db.Column(db.String, nullable=False)
    headsign = db.Column(db.String, nullable=False)
    long_name = db.Column(db.String, nullable=False)
    website = db.Column(db.String, nullable=False)
    latitude = db.Column(db.String, nullable=False)
    longitude = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)


    @property
    def serialize(self):
        return {
            "time": self.time,
            "mode": self.mode,
            "destination": self.long_name,
            "website": self.website,
            "latitude": self.latitude,
            "longitude": self.longitude
        }
    