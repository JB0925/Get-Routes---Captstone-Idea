# Ride Finder

### Test Out Ride Finder

The following username and password combinations have been created for convenience and so that you can skip the sign up process if you would like to try out Ride Finder:
- **Username**: testing123, **Password**: password
- **Username**: testuser, **Password**: password
- **Username**: tryitout, **Password**: password

### Find Rides Near You

This project is my first capstone for the Springboard Software Engineering Program. It aims to find public transit routes within a 500 meter radius of an address that a user gives. From there, it finds stations that are located within that 500 meter radius (if any). If you click a station, it will render a map of the next five departures from that station, as well as give some information about each departure. The map, while fairly accurate, is not intended to be read as the exact location of the stop. Rather, it will give you a general idea as to where the route would take you.

## How to Use or View Ride Finder
The easiest way to view and try out Ride Finder is by visiting the page deployed on [heroku]. You could also clone this repo and run it locally by:
- setting up a virtual environment
- pip installing the requirements.txt file dependencies
- setting up a database
- getting the necessary API keys from HERE, Google, and Mapquest (see the .env.example file)

## How Ride Finder Was Built
Ride Finder was created with several different technologies. They include:
- Python
- JavaScript
- HTML5
- CSS3
- Mapquest.js
- Google's Geocoding API
- The HERE Public Transit API
- PostgreSQL

   [heroku]: <http://find-rides.herokuapp.com>

## Tests
Ride Finder's tests were written in Python with the Unittest framework. They can be run by:
1). Creating a virtual environment
2). Installing all dependencies with **pip install -r requirements.txt**
3). Running the following command: **python3 -m unittest -v**
   

