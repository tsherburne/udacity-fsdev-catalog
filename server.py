from flask import Flask, render_template, request, redirect, jsonify
from flask import make_response, url_for, flash, session as login_session

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, Category, Item

import flask
import os
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Connect to the database and create a session
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['openid']

app = Flask(__name__)

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
    
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    
    # Store the state so the callback can verify the auth server response.
    flask.session['state'] = state
    
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    state = flask.session['state']
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)
    
    # Use the authorization server's response to fetch the OAuth 2.0 tokens.
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    # Store credentials in the session.
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)
    
    return flask.redirect(flask.url_for('routeCatalog'))

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

# Upon logout - clear credentials    
@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return redirect(url_for('routeCatalog'))

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
    # When running locally, disable OAuthlib's HTTPs verification.
    # ACTION ITEM for developers:
    #     When running in production *do not* leave this option enabled.
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
    