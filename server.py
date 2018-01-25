from flask import Flask, render_template, request, redirect, jsonify
from flask import make_response, url_for, flash, session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Connect to the database and create a session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)

# Load secrets for Google OAuth usage
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

# Create anti-forgery state token for login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def login():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output
    
@app.route('/logout')
def gdisconnect():
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: ' 
    print login_session['username']
    if access_token is None:
 	print 'Access Token is None'
    	response = make_response(json.dumps('Current user not connected.'), 401)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
	del login_session['access_token'] 
    	del login_session['gplus_id']
    	del login_session['username']
    	del login_session['email']
    	del login_session['picture']

    	response = make_response(json.dumps('Successfully disconnected.'), 200)
    	response.headers['Content-Type'] = 'application/json'
    	return response
    else:
	
    	response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    	response.headers['Content-Type'] = 'application/json'
    	return response


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
    