from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import(TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
import random, string

Base = declarative_base()
secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))

# Creates a table for update information
class SoftwareUpdate(Base):
    __tablename__ = 'softwareUpdate'

    id = Column(Integer, primary_key = True)
    versionNumber = Column(String(10))
    nameUpdate =Column(String(80))
    newFeatures = Column(String(250))
    bugFixes = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
          'id': self.id,
       		'versionNumber': self.versionNumber,
          'nameUpdate': self.nameUpdate,
          'newFeatures' : self.newFeatures,
          'bugFixes' : self.bugFixes
       }

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=60000):
      s = Serializer(secret_key, expires_in = expiration)
      return s.dumps({'id': self.id })

    @staticmethod
    def verify_auth_token(token):
      s = Serializer(secret_key)
      try:
        data = s.loads(token)
      except SignatureExpired:
        #Valid Token, but expired
        return None
      except BadSignature:
        #Invalid Token
        return None
      user_id = data['id']
      return user_id

 
engine = create_engine('sqlite:///softwareUpdate.db')
Base.metadata.create_all(engine)

