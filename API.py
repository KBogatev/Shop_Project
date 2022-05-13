from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://Shop_Database:root@172.17.0.2:65529/shop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
@app.route('/')
def index():
    return 'Hello!'


class Users(db.model):
    id = db.Column(db.integer, primary_key = True, auto_increment = True, nullable = False)
    first_name = db.Column(db.String(80), nullable = False)
    last_name = db.Column(db.String(80))
    joined_at = db.Column(db.TIMESTAMP(datetime.now()))

class Products(db.model):
    id = db.Column(db.integer, primary_key = True, nullable = False)
    name = db.Column(db.String(100), nullable = False)
    created_at = db.Column(db.TIMESTAMP(datetime.now()))
    sell_state = db.Column(db.Boolean)
