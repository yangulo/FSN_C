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

countryFlag1 = session.query(Countries).filter_by(id = 1).one()
countryFlag2 = session.query(Countries).filter_by(id = 2).one()
countryFlag3 = session.query(Countries).filter_by(id = 3).one()
countryFlag4 = session.query(Countries).filter_by(id = 4).one()
countryFlag5 = session.query(Countries).filter_by(id = 5).one()

countryFlag1.flag = "australia.jpg"
countryFlag2.flag = "canada.jpg"
countryFlag3.flag = "us.jpg"
countryFlag4.flag = "greece.jpg"
countryFlag5.flag = "france.jpg"

session.add(countryFlag1)
session.add(countryFlag2)
session.add(countryFlag3)
session.add(countryFlag4)
session.add(countryFlag5)

session.commit()
print "images added!"
