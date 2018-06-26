from flask import Flask, request, jsonify, make_response, abort, render_template, json, g, redirect, url_for, request
from models import User
from flask_httpauth import HTTPBasicAuth
from functions import *
from RateLimit import *

"""
    Filename: endpoints.py
    Python Version: 3.6
    Author: Zemann Sheen
    Date created: June 20, 2018
    Date last modified: June 26, 2018

    endpoints.py contains all the endpoints for both 
    frontend web and backend requests. All these
    endpoints build on top of the app flask framework.

    Add all new endpoints here and to run the API, 
    simply run this endpoints.py file

"""

auth = HTTPBasicAuth()
app = Flask(__name__, template_folder="templates")

""" WEB FRONTEND ENDPOINTS """
# Login window
@app.route("/")
@app.route("/login")
def home():
    return render_template('index.html')


# Sign Up new user window
@app.route('/showSignUp')
def show_sign_up():
    return render_template('signup.html')


# The backend for the sign up window for when the sign up button is clicked
@app.route('/signUp', methods=['POST'])
def sign_up():
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']

    return addNewUser(_name, _password)


# The backend for the sign in window for when the sign in button is clicked
@app.route('/signIn', methods=['POST'])
def sign_in():
    _name = request.form['inputName']
    _password = request.form['inputPassword']

    if verify_password(_name, _password):
        return jsonify({'Login Status': 'True'}), 200

    return jsonify({'Login Status': 'False'}), 301


# The main homepage after logging in, if the credentials of the sign in is valid, then show home
@app.route('/home')
@auth.login_required
def home_page():
    return render_template('home.html')


""" CURL Backend API Endpoints """


# checks if a user exists, returns just the username
@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})


# verifys if a password is correct, needs authentication
@auth.verify_password
@ratelimit(limit=10, per=60 * 1)
def verify_password(username_or_token, password):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# Endpoint for getting the all the past version information or posting a new update
@app.route("/version", methods=['GET', 'POST'])
@auth.login_required
@ratelimit(limit=30, per=60 * 1)
def version_number_function():
    if request.method == 'GET':
        return getAllVersion()

    elif request.method == 'POST':
        if not request.json or not 'versionNumber' in request.json:
            abort(400)

        version_number = request.json["versionNumber"]
        name_update = request.json["nameUpdate"]
        new_features = request.json["newFeatures"]
        bug_fixes = request.json["bugFixes"]
        return addNewUpdate(version_number, name_update, new_features, bug_fixes)


# the endpoint for getting just the latest update information quickly
@app.route("/version/latest", methods=['GET'])
@auth.login_required
@ratelimit(limit=30, per=60 * 1)
def latest_version():
    if request.method == 'GET':
        return getLatestVersion()


# the endpoint for getting the latest version number for checks
@app.route("/version/latest/number", methods=['GET'])
@auth.login_required
@ratelimit(limit=100, per=60 * 1)
def latest_version_number():
    if request.method == 'GET':
        return getLatestVersionNumber()


# Endpoint for getting a specific version number, editing, or to delete a version number
@app.route("/version/<int:id>", methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
@ratelimit(limit=30, per=60 * 1)
def version_function_id(id):
    if request.method == 'GET':
        return getVersion(id)

    elif request.method == 'PUT':
        if not request.json or not 'versionNumber' in request.json:
            abort(400)

        version_number = request.json["versionNumber"]
        name_update = request.json["nameUpdate"]
        new_features = request.json["newFeatures"]
        bug_fixes = request.json["bugFixes"]
        return updateDescr(id, version_number, name_update, new_features, bug_fixes)

    elif request.method == 'DELETE':
        return deleteUpdate(id)


# Gives the User a token so that they only need to login once
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# Adds a new user to database and encrypts
@app.route('/api/users', methods=['POST'])
def new_user():
    if request.method == 'POST':
        if not request.json or not 'username' in request.json:
            abort(400)

        username = request.json['username']
        password = request.json['password']

        return addNewUser(username, password)


""" RATE LIMITER TEST """


# After the request, notifies user how many send requests left
@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response


# Test resource to be accessed in rate limit test
@app.route('/rate-limited')
@ratelimit(limit=30, per=60 * 1)
def index():
    return jsonify({'response': 'This is a rate limited response'})


""" ERROR HANDLERS """


# Handles error 404 so it returns JSON instead of HTML message
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request. Missing data or version number.'}), 400)


@app.errorhandler(401)
def bad_request(error):
    return make_response(jsonify({'error': 'Authentication Required: Data protected.'}), 401)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
