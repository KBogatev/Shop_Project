from flask import Flask, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, DateTime
from sqlalchemy.sql import func
app = Flask(__name__)
import os
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

url = "mysql://root:root@localhost:52000"
engine = create_engine(url)
create_str = "CREATE DATABASE IF NOT EXISTS shop_db;"
engine.execute(create_str)
engine.execute("USE shop_db;")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:52000/shop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

Sales = db.Table('Sales',
    db.Column('id', db.Integer, primary_key = True, nullable = False),
    db.Column('user_id', db.Integer, db.ForeignKey('Users.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
    db.Column('sell_date', DateTime(timezone=True), server_default=func.now(), nullable = False)
)
    

class users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column(db.String(80), nullable = False)
    last_name = db.Column(db.String(80), nullable = False)
    joined_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    buyers = db.relationship('products', secondary=Sales, lazy='subquery',
        backref=db.backref('users', lazy=True))

    def __repr__(self):
        return f'User:{self.first_name} {self.last_name}'
        
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

class products(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column('Name', db.String(100), nullable = False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    sell_state = db.Column(db.Boolean, nullable = False)

db.create_all()
db.session.commit()

def add_users():
    first_name = str(input('Enter your first name.'))
    last_name = str(input('Enter your last name.'))
    new_user = users(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

@app.route('/')
def index():
    return 'Hello, welcome to our shop!'

@app.route('/register', methods = ['GET', 'PUT'])
def register():
    try:
        add_users()
    except ValueError:
        flash('Oops! It seems an error has occured, please try again.')
    return redirect(url_for('index'))

@app.route('/users', methods = ['GET'])
def get_users():
    users.Query.all()
    
    return None

        




