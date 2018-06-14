from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

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

 
engine = create_engine('sqlite:///softwareUpdate.db')
Base.metadata.create_all(engine)

