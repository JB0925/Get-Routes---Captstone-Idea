# Ride Finder Database Schema

### Users table
id (SERIAL, pk)
username (VARCHAR, NOT NULL UNIQUE)
password (VARCHAR NOT NULL)
email (VARCHAR UNIQUE, NOT NULL)

- Will have a "searches" relationship to a coming table, called "searches", where you can get info on a user's previous searches.
- Will have a __str__ method to make the user object easy to read.
- Will have the @classmethod's "register" to sign up a new user, and "authenticate" to ensure that a user has the proper credentaisl to access a page or area of content.

### Search table
id(SERIAL, pk)
time(VARCHAR)
transportation_mode(VARCHAR)
destination(VARCHAR)
website(VARCHAR)
user_id(INTEGER, REFERENCES users(id))

- Will have a serialize method that allows us to easily turn query data into JSON format

### Origin table
id (pk, SERIAL)
city_and_state(VARCHAR NOT NULL)
latitude(VARCHAR NOT NULL)
longitude(VARCHAR NOT NULL)

-Will have a serialize method that allows us to easily turn query data into JSO
N format


### Station table
id(SERIAL, pk)
name(VARCHAR NOT NULL)
station_latitude(VARCHAR, NOT NULL)
station_longitude(VARCHAR NOT NULL)

-Will have a serialize method that allows us to easily turn query data into JSO
N format

- Will have a "batch_commit" method that runs a for loop and commits each instance of new station data to the database, rather than completing the entire process in route (less messy).


### StationDirections table
id(pk SERIAL)
directions(TEXT)

- Also contains the batch commit method for convenience.



### RouteData table
id(pk,SERIAL)
time(VARCHAR NOT NULL)
name(VARCHAR NOT NULL)
mode(VARCHAR NOT NULL)
bus_headsign, long_form_route_name, website, latitude, longitude...(VARCHAR NOT NULL)


# Most of the tables in this schema are more for collecting large amounts or data, creating ways to manipulate that data, and packaging it up to be sent as a JSON response to the client-side.
