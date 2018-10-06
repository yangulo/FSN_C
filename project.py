from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from sqlalchemy import create_engine, asc, and_
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Countries, Places, Activities, Users
from flask import session as login_session
import random
import string
import json
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "My Catalog Project"


# Connect to the Database and create database session
# engine = create_engine('sqlite:///coutriescatalog.db')
engine = create_engine('sqlite:///coutriescatalogwithusers.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    print('stored_access_token', stored_access_token)
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    print(credentials)
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(answer.json())

    # login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['email']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px; '
    output += 'border-radius: 150px; -webkit-border-radius: 150px; '
    output += '-moz-border-radius: 150px;">'
    # For future implementation flash message
    print "done!"
    return output


# User Helper Functions
def createUser(login_session):
    newUser = Users(email=login_session[
        'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    print('access_token', access_token)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print(result['status'])
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        # del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Home
# Show all countries
@app.route('/')
@app.route('/countries/')
def showCountries():
    countries = session.query(Countries).order_by(asc(Countries.name))
    if 'email' not in login_session:
        return render_template('countries.html', countries=countries)
    if 'email' in login_session:
        return render_template('countriesloggedin.html', countries=countries)


# Show all places
@app.route('/country/<int:country_id>/')
def showPlaces(country_id):
    c = session.query(Countries).filter_by(id=country_id).one()
    places = session.query(Places).filter_by(country_id=country_id).all()
    return render_template(
        'places.html', c=c, places=places)


# Show activities to do in each place
@app.route('/country/<int:country_id>/placeid/<int:place_id>/')
def showActivities(country_id, place_id):
    activities = {}
    country = session.query(Places).filter_by(id=place_id).one()
    if country_id == country.country_id:
        activities = session.query(Activities).filter_by(
            place_id=place_id).all()
        for activity in activities:
            # creator = getUserInfo(activity['user_id'])
            if ('email' in login_session
                    and activity.user_id == login_session['user_id']):
                return render_template('activities.html',
                                       activities=activities,
                                       country=country)
        return render_template('activitiespublic.html', activities=activities,
                               country=country)
    else:
        return "There are no activities associated to that Country/Place"


# Add new thing to do per place
@app.route('/country/<int:country_id>/placeid/<int:place_id>/new',
           methods=['GET', 'POST'])
def addNewActivity(country_id, place_id):
    newActivity = {}
    country = session.query(Places).filter_by(id=place_id).one()
    if 'email' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        if country_id == country.country_id:
            newActivity = Activities(name=request.form['name'],
                                     description=request.form['description'],
                                     place_id=place_id,
                                     user_id=login_session['user_id'])
            session.add(newActivity)
            # # For future implementation flash message
            session.commit()
            return redirect(url_for('showActivities', country_id=country_id,
                                    place_id=place_id))
    else:
        return render_template('newActivity.html', country_id=country_id,
                               place_id=place_id, country=country)


# Edit each thing to do per place
@app.route('/country/<int:country_id>/placeid/<int:place_id>/activityid/'
           + '<int:activity_id>/edit',
           methods=['GET', 'POST'])
def editActivity(country_id, place_id, activity_id):
    country = session.query(Places.country_id).filter_by(id=place_id).one()
    place = session.query(Activities.place_id).filter_by(id=activity_id).one()
    p_c = session.query(Places.country_id).filter_by(id=place[0]).one()
    editedActivity = session.query(Activities).filter_by(id=activity_id).one()
    if 'email' not in login_session:
        return redirect('/login')
    if editedActivity.user_id != login_session['user_id']:
        output = ""
        output += "<script>function myFunction() {alert('You are not "
        output += "authorized to edit this activity. Please create your own "
        output += "activity to edit');}</script><body onload='myFunction()''>"
        return output
    if request.method == 'POST':
        if country[0] == p_c[0]:
            if request.form['name']:
                editedActivity.name = request.form['name']
            if request.form['description']:
                editedActivity.description = request.form['description']
            session.add(editedActivity)
            session.commit()
            # # For future implementation flash message
            return redirect(url_for('showActivities', country_id=country_id,
                                    place_id=place_id))
    else:
        return render_template('editActivity.html',
                               country_id=country_id, place_id=place_id,
                               activity_id=activity_id,
                               editedActivity=editedActivity)


# Delete each thing to do per place
@app.route('/placeid/<int:place_id>/activityid/<int:activity_id>/delete',
           methods=['GET', 'POST'])
def deleteActivity(place_id, activity_id):
    country_id = session.query(Places.country_id).filter_by(id=place_id).one()
    place = session.query(Activities.place_id).filter_by(id=activity_id).one()
    activityToDelete = session.query(
        Activities).filter_by(id=activity_id).one()
    if 'email' not in login_session:
        return redirect('/login')
    if activityToDelete.user_id != login_session['user_id']:
        output = ""
        output += "<script>function myFunction() {alert('You are not "
        output += "authorized to delete this activity. Please ensure "
        output += "you are looking at your own activities in order to"
        output += " delete.');}</script><body onload='myFunction()''>"
        return output
    if request.method == 'POST':
        if place[0] == place_id:
            session.delete(activityToDelete)
            session.commit()
            # # For future implementation flash message
            return redirect(url_for('showActivities',
                                    country_id=country_id[0],
                                    place_id=place_id))
    else:
        return render_template('delete_activity.html',
                               country_id=country_id[0],
                               activityToDelete=activityToDelete)


# JSON
# Show all contries JSON
@app.route('/JSON')
@app.route('/countries/JSON')
def allContriesJSON():
    countries = session.query(Countries).all()
    return jsonify(countries=[c.serialize for c in countries])


# Show all places JSON
@app.route('/places/JSON')
def allPlacesJSON():
    places = session.query(Places).all()
    return jsonify(places=[p.serialize for p in places])


# Show all activities JSON
@app.route('/activities/JSON')
def allActivitiesJSON():
    activities = session.query(Activities).all()
    return jsonify(activities=[a.serialize for a in activities])


# Show places within a country JSON
@app.route('/country/<int:country_id>/JSON')
def placeInCountryJSON(country_id):
    places = session.query(Places).filter_by(country_id=country_id).all()
    return jsonify(places=[p.serialize for p in places])


# Show activities within a place within a country JSON
@app.route('/country/<int:country_id>/placeid/<int:place_id>/JSON')
def activityInPlaceJSON(country_id, place_id):
    activities = {}
    country = session.query(Places).filter_by(id=place_id).one()
    if country_id == country.country_id:
        activities = session.query(Activities).filter_by(
            place_id=place_id).all()
        return jsonify(activities=[a.serialize for a in activities])
    else:
        return "There are no activities associated to that Country/Place"


# Always at end of file !Important!
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
