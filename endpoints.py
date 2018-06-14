from flask import Flask, request, jsonify, make_response, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, SoftwareUpdate

# the database to connect to
engine = create_engine('sqlite:///softwareUpdate.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__) 

# the route get or post for the version number or to add a version number (Need to edit POST to work with curl)
# curl -i -H "Content-Type: application/json" -X POST -d '{"versionNumber":"1.0.0", "nameUpdate":"Version 1", "newFeatures":"None", "bugFixes":"None"}' http://127.0.0.1:5000/version
@app.route("/")
@app.route("/version", methods = ['GET', 'POST'])
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
def latestVersion():
  if request.method == 'GET':
    return getLatestVersion()


# the endpoint for getting the latest version number for checks
@app.route("/version/latest/number", methods = ['GET'])
def latestVersionNumber():
  if request.method == 'GET':
    return getLatestVersionNumber()
 
  
# Endpoint for getting a specific version number, editing, or to delete a version number
@app.route("/version/<int:id>", methods = ['GET', 'PUT', 'DELETE'])
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


# Gets the latest version number
def getAllVersion():
  version = session.query(SoftwareUpdate).all()
  return jsonify(SoftwareUpdate=[i.serialize for i in version])

# gets the specific version number passed in
def getVersion(id):
  try:
    update = session.query(SoftwareUpdate).filter_by(id = id).one()
    return jsonify(update=update.serialize) 
  except:
    abort(404)

  
# Gets called when a POST request is sent
def addNewUpdate(versionNumber, nameUpdate, newFeatures, bugFixes):
  update = SoftwareUpdate(versionNumber = versionNumber, nameUpdate = nameUpdate, newFeatures = newFeatures, bugFixes = bugFixes)
  session.add(update)
  session.commit()
  return jsonify(SoftwareUpdate=update.serialize)

# Gets the latest version of update
def getLatestVersion():
  update = session.query(SoftwareUpdate).order_by(SoftwareUpdate.id.desc()).first()
  return jsonify(SoftwareUpdate=[update.serialize])

# Gets the latest version number of update
def getLatestVersionNumber():
  update = session.query(SoftwareUpdate).order_by(SoftwareUpdate.id.desc()).first()
  versionNumber = update.versionNumber
  print(versionNumber)
  return jsonify(versionNumber=versionNumber)

# Updates the update information
def updateDescr(id, versionNumber, nameUpdate, newFeatures, bugFixes):
  update = session.query(SoftwareUpdate).filter_by(id = id).one()
  if not versionNumber:
    update.versionNumber = versionNumber
  if not nameUpdate:
    update.nameUpdate = nameUpdate
  if not newFeatures:
    update.newFeatures = newFeatures
  if not bugFixes:
  	update.bugFixes = bugFixes
  session.add(update)
  session.commit()
  return "Updated description for version number %s" % versionNumber

# Removes an update
def deleteUpdate(id):
  update = session.query(SoftwareUpdate).filter_by(id = id).one()
  session.delete(update)
  session.commit()
  return "Removed update with version number %s" % versionNumber




#SECURITY so that not anyone can add or get the information in the API
@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing arguments
    if session.query(User).filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username = username)
    user.hash_password(password)
    session.add(user)
    session.commit()
    return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/users/<int:id>')
def get_user(id):
    user = session.query(User).filter_by(id=id).one()
    if not user:
        abort(400)
    return jsonify({'username': user.username})




# Handles error 404 so it returns JSON instead of HTML message
@app.errorhandler(404)
def not_found(error):
  return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
  return make_response(jsonify({'error': 'Bad request. Missing data or version number.'}), 400)


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=5000)	

