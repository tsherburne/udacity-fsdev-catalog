from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db_setup import Category, Base, Item, User

# Connect to database and initialize 'session'
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Add Admin User
u1 = User(name="DB Admin", google_id=0)

# Add Categories
c1 = Category(name="Doors")
session.add(c1)

c2 = Category(name="Lumber")
session.add(c2)

c3 = Category(name="Plywood")
session.add(c3)

c4 = Category(name="Decking")
session.add(c4)

session.commit()

# Add initial Items
i1 = Item(name="Raised Panel", description="Classic Look",
          category=c1, user=u1)
i2 = Item(name="Flat Panel", description="Traditional Look",
          category=c1, user=u1)

i3 = Item(name="2x4", description="Wall Framing",
          category=c2, user=u1)
i4 = Item(name="2x10", description="Floor Joists",
          category=c2, user=u1)

i5 = Item(name="4x8 Flooring", description="Finished One Side",
          category=c3, user=u1)
i6 = Item(name="4x8 Cherry", description="Finished Both Sides",
          category=c3, user=u1)

i7 = Item(name="Trex", description="No maintenance",
          category=c4, user=u1)
i8 = Item(name="Cedar", description="Natural finish",
          category=c4, user=u1)

session.add(i1)
session.add(i2)
session.add(i3)
session.add(i4)
session.add(i5)
session.add(i6)
session.add(i7)
session.add(i8)

session.commit()


print "added categories and items to db"
