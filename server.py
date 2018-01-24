from flask import Flask, render_template, request, redirect, jsonify
from flask import make_response, url_for, flash, session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item


# Connect to the database and create a session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Show catalog and item list for selected category
@app.route('/catalog/<int:category_id>/')
def showCatalog(category_id):
    print login_session
    print category_id

    if 'username' in login_session:
        del login_session[ 'username' ]
    else:
        login_session[ 'username' ] = "tims"
      
    sel_cat = session.query(Category).filter_by(id=category_id).one_or_none()
  
    if sel_cat is not None:
        login_session[ 'sel_cat'] = sel_cat.name
    else:
        if 'sel_cat' in login_session:
            del login_session[ 'sel_cat']
        print("Doing Redirect /")
        return redirect(url_for('routeCatalog'))
        
    categories = session.query(Category).order_by(asc(Category.name))

    items = session.query(Item).filter_by(category_id=category_id).order_by(asc(Item.name)).all()

    return render_template('catalog.html', categories=categories, items=items)
    
# Redirect to catalog, showing item list for 'first' catalog entry
@app.route('/')
def routeCatalog():
    category = session.query(Category).order_by(asc(Category.name)).first()
    category_id = category.id
    print("Doing Redirect: " + str(category_id))
    return redirect(url_for('showCatalog', category_id=category_id))
    
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
    