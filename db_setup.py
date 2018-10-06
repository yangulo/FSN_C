import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Base class to inheret from
Base = declarative_base()

# User class
class Users(Base):
    __tablename__ = 'users'

    id = Column(
        Integer,
        primary_key=True
    )
    email = Column(
        String(350),
        nullable=False
    )
    picture = Column(
        String(250)
    )


# Countries class
class Countries(Base):
    __tablename__ = 'countries'

    name = Column(
        String(50),
        nullable=False
    )
    flag = Column(
        String(100)
    )
    id = Column(
        Integer,
        primary_key=True
    )
    

# JSON
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'flag': self.flag
        }


# Places class
class Places(Base):
    __tablename__ = 'places'

    name = Column(
        String(50),
        nullable=False
    )
    id = Column(
        Integer,
        primary_key=True
    )
    country_id = Column(
        Integer,
        ForeignKey('countries.id')
    )
    countries = relationship(Countries)


# JSON
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'country_id': self.country_id
        }


# Activities class
class Activities(Base):
    __tablename__ = 'activities'

    name = Column(
        String(70),
        nullable=False
    )
    id = Column(
        Integer,
        primary_key=True
    )
    description = Column(
        String(500)
    )
    image = Column(
        String(8)
    )
    place_id = Column(
        Integer,
        ForeignKey('places.id')
    )
    places = relationship(Places)
    
    user_id = Column(
        Integer,
        ForeignKey('users.id')
    )
    users = relationship(Users)


# JSON
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'image': self.image,
            'place_id': self.place_id,
            'user_id': self.user_id
        }


# To connect to the Database
# engine = create_engine('sqlite:///coutriescatalog.db')
engine = create_engine('sqlite:///coutriescatalogwithusers.db')
Base.metadata.create_all(engine)

