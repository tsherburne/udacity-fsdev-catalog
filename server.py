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

# Update Item in Database
@app.route('/updateItem/<int:item_id>', methods=['POST'])
def updateItem(item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.category_id = request.form['category']
        session.add(item)
        session.commit()
        flash('Item Updated')
    except:
        flash('Item not found')

    return redirect(url_for('editItem', mode="e", item_id=item.id))
 
# Delete Item from Database
@app.route('/deleteItem/<int:item_id>', methods=['POST'])
def deleteItem(item_id):
    try:
        item = session.query(Item).filter_by(id=item_id).one()
        session.delete(item)
        session.commit()
        flash('Item deleted')
    except:
        flash('Item not found')
    return redirect(url_for('routeCatalog'))

# Create Item in Database
@app.route('/createItem', methods=['POST'])
def createItem():
    try:
        print request.form
        
        item = Item(name=request.form['name'], 
                    description=request.form['description'], 
                    category_id=request.form['category'])
                    
        session.add(item)
        session.commit()
        flash('Item Created')
    except:
        flash('Create failed')

    return redirect(url_for('routeCatalog'))


# Edit Item
@app.route('/item/<string:mode>/<int:item_id>/')
def editItem(mode, item_id):
    if mode != "a" and mode != "e":
        return redirect(url_for('routeCatalog'))

    if mode == "e":
        try:
            item = session.query(Item).filter_by(id=item_id).one()
        except:
            return redirect(url_for('routeCatalog'))
    else:
        item = None
        
    return render_template('item.html', mode=mode, item=item)


# Show catalog and item list for selected category
@app.route('/catalog/<int:category_id>/')
def showCatalog(category_id):
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
        return redirect(url_for('routeCatalog'))
        
    categories = session.query(Category).order_by(asc(Category.name))
    # Select Items for "selected" Category
    items = session.query(Item).filter_by(category_id=category_id).\
                order_by(asc(Item.name)).all()

    return render_template('catalog.html', categories=categories, items=items)
    
# Redirect to catalog, showing item list for 'first' catalog entry
@app.route('/')
def routeCatalog():
    category = session.query(Category).order_by(asc(Category.name)).first()
    category_id = category.id
    return redirect(url_for('showCatalog', category_id=category_id))
    
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
    