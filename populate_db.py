from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Category, Base, Item

#Connect to database and initialize 'session'
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

#Add Categories
c1 = Category(name="Doors")
session.add(c1)

c2 = Category(name="Lumber")
session.add(c2)

c3 = Category(name="Plywood")
session.add(c3)

c4 = Category(name="Decking")
session.add(c4)

session.commit()

#Add initial Items
i1=Item(name="Raised Panel", description="Classic Look", category=c1)
session.add(i1)

session.commit();


print "added categories and items to db"
