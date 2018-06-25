from flask import Flask, request, jsonify, make_response, abort, render_template, json, g
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from models import Base, SoftwareUpdate, User
from flask_httpauth import HTTPBasicAuth
from flask_login import LoginManager
from redis import Redis
redis = Redis()
import time
from functools import update_wrapper

engine = create_engine('sqlite:///softwareUpdate.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

### FUNCTIONS: Endpoints call these functions for the core functionality ###

def add_new_user(username, password):
  if username is None or password is None:
        abort(400) # missing arguments
  if session.query(User).filter_by(username = username).first() is not None:
        abort(400) # existing user

  user = User(username = username)
  user.hash_password(password)
  session.add(user)
  session.commit()
  return jsonify({ 'username': user.username }), 201


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


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
