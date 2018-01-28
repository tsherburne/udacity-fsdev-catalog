## Wood Products Catalog
This respository is for project #4 (Catalog DB with data-driven Web UI) 
for the [Udacity Fullstack Developers Nano Degree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).
### Table of Contents

* [Installation](#installation)
* [Setup](#setup)
* [Running](#running)

### Installation
Clone the respository:

```
https://github.com/tsherburne/udacity-fsdev-catalog.git
cd udacity-fsdev-catalog
```

### Setup
Initalize and populate the sample database.
```
python db_setup.py
phthon populate_db.py
```
Using Google Developer Account, enable a test project and create account credentials.
https://console.developers.google.com/

The `client_secrets.json` needs to be downloaded from Google and stored in the same directory as the `server.py` to enable Google Authentication

The OAuth authentication flow in this project leverages the Google Python Tutorial.
See: https://developers.google.com/identity/protocols/OAuth2WebServer

By default the Web Server listens on port 8080.  If desired, the port can be updated in `server.py`
### Running

Start the Web Server:
```
python server.py
```

Open a browser and to view and update the Wood Products Catalog!
```
https://<host>:8080
```

The Catalog can be browsed without logging in, but modification (Create / Update / Delete) of an item requires login. Buttons in the right hand corner of the header provide login / logout functions. Additionally, only the user who creates an item can later update or delete that item.

A JSON endpoint is provided to retrive an item from the catalog.
```
https://<host>:8080/api/item/<item_id>/JSON
```