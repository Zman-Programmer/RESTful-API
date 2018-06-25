from flask import Flask, request, jsonify, make_response, abort, render_template, json, g
from models import Base, SoftwareUpdate, User
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from redis import Redis
redis = Redis()
import time
from functions import *
from functools import update_wrapper


auth = HTTPBasicAuth() 

app = Flask(__name__, template_folder="templates") 


@app.route("/")
@app.route("/login")
def home():
  return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST'])
def signUp():
 
    # read the posted values from the UI
    _name = request.form['inputName']
    _email = request.form['inputEmail']
    _password = request.form['inputPassword']
 
    # validate the received values
    return add_new_user(_name, _password)

@app.route('/signIn', methods=['POST'])
def signIn():
    #read in the username and password
    _name = request.form['inputName']
    _password = request.form['inputPassword']

    if(verify_password(_name, _password) == True):
      return jsonify({ 'Login Status': 'True' }), 200
    
    return jsonify({ 'Login Status': 'False' }), 301


@app.route('/home')
def homePage():
  return render_template('home.html')

@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@auth.verify_password
def verify_password(username_or_token, password):
    #Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id = user_id).one()
    else:
        user = session.query(User).filter_by(username = username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# the route get or post for the version number or to add a version number (Need to edit POST to work with curl)
# curl -i -H "Content-Type: application/json" -X POST -d '{"versionNumber":"1.0.0", "nameUpdate":"Version 1", "newFeatures":"None", "bugFixes":"None"}' http://127.0.0.1:5000/version
@app.route("/version", methods = ['GET', 'POST'])
@auth.login_required
def versionNumberFunction():
  if request.method == 'GET':
    return getAllVersion()

  elif request.method == 'POST':
    if not request.json or not 'versionNumber' in request.json:
      abort(400)

    versionNumber = request.json["versionNumber"]
    nameUpdate = request.json["nameUpdate"]
    newFeatures = request.json["newFeatures"]
    bugFixes = request.json["bugFixes"]
    return addNewUpdate(versionNumber, nameUpdate, newFeatures, bugFixes)

# the endpoint for getting the latest update information quickly
@app.route("/version/latest", methods = ['GET'])
@auth.login_required
def latestVersion():
  if request.method == 'GET':
    return getLatestVersion()


# the endpoint for getting the latest version number for checks
@app.route("/version/latest/number", methods = ['GET'])
@auth.login_required
def latestVersionNumber():
  if request.method == 'GET':
    return getLatestVersionNumber()
 
  
# Endpoint for getting a specific version number, editing, or to delete a version number
@app.route("/version/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
@auth.login_required
def versionFunctionId(id):
  if request.method == 'GET':
    return getVersion(id)

  elif request.method == 'PUT':
    if not request.json or not 'versionNumber' in request.json:
      abort(400)

    versionNumber = request.json["versionNumber"]
    nameUpdate = request.json["nameUpdate"]
    newFeatures = request.json["newFeatures"]
    bugFixes = request.json["bugFixes"]
    return updateDescr(id, versionNumber, nameUpdate, newFeatures, bugFixes)
    
  elif request.method == 'DELETE':
    return deleteUpdate(id)

# Gives the User a token so that they only need to login once
# curl -u username:password -i http://127.0.0.1:5000/token
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


#SECURITY so that not anyone can add or get the information in the API
@app.route('/api/users', methods = ['POST'])
def new_user():
  if request.method == 'POST':
    if not request.json or not 'username' in request.json:
        abort(400)

    username = request.json['username']
    password = request.json['password']

    return add_new_user(username, password)


### ERROR HANDLERS ###
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


"""@app.after_request
def inject_x_rate_headers(response):
    limit = get_view_rate_limit()
    if limit and limit.send_x_headers:
        h = response.headers
        h.add('X-RateLimit-Remaining', str(limit.remaining))
        h.add('X-RateLimit-Limit', str(limit.limit))
        h.add('X-RateLimit-Reset', str(limit.reset))
    return response

@app.route('/rate-limited')
@ratelimit(limit=5, per=30 * 1)
def index():
    return jsonify({'response':'This is a rate limited response'})"""




if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = False
    app.run(host='0.0.0.0', port=5000)	

