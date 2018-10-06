from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Countries, Places, Activities, Users

# engine = create_engine('sqlite:///coutriescatalog.db')
engine = create_engine('sqlite:///coutriescatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Users
User1 = Users(email="yadira.alvarez.angulo@gmail.com")
session.add(User1)

# COUNTRIES
Australia = Countries(name="Australia")
Canada = Countries(name="Canada")
US = Countries(name="United States")
Greece = Countries(name="Greece")
France = Countries(name="France")
session.add(Australia)
session.add(Canada)
session.add(US)
session.add(Greece)
session.add(France)

# PLACES

# Australia
Australia_Sydney = Places(
    name="Sydney",
    countries=Australia)
Australia_Cairns = Places(
    name="Cairns",
    countries=Australia)
session.add(Australia_Sydney)
session.add(Australia_Cairns)

# Canada
Canada_Vancouver = Places(
    name="Vancouver",
    countries=Canada)
session.add(Canada_Vancouver)

# United States
US_California = Places(
    name="California",
    countries=US)
session.add(US_California)

# Greece
Greece_Zakynthos = Places(
    name="Zakynthos",
    countries=Greece)
Greece_Santorini = Places(
    name="Santorini",
    countries=Greece)
Greece_Athens = Places(
    name="Athens",
    countries=Greece)
session.add(Greece_Zakynthos)
session.add(Greece_Santorini)
session.add(Greece_Athens)

# France
France_Paris = Places(
    name="Paris",
    countries=France)
session.add(France_Paris)

# ACTIVITIES

# Australia
Sydney_a1 = Activities(
    name="Opera House",
    description="Opera House tour",
    places=Australia_Sydney,
    users=User1)
Sydney_a2 = Activities(
    name="Taronga Zoo",
    description="Taronga Zoo",
    places=Australia_Sydney,
    users=User1)
Sydney_a3 = Activities(
    name="Blue Mountains",
    description="Blue Mountains tour",
    places=Australia_Sydney,
    users=User1)
Cairns_a4 = Activities(
    name="Great Barrier Reef",
    description="Great Barrier Reef experience",
    places=Australia_Cairns,
    users=User1)
Cairns_a5 = Activities(
    name="Kuranda",
    description="Kuranda Gondola",
    places=Australia_Cairns,
    users=User1)
session.add(Sydney_a1)
session.add(Sydney_a2)
session.add(Sydney_a3)
session.add(Cairns_a4)
session.add(Cairns_a5)

session.commit()
print "added menu items!"

