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

