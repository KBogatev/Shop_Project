from flask import Flask, request, flash, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import InputRequired
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

class RegistrationForm (FlaskForm):
    first_name = StringField('First name', validators = [InputRequired()])
    last_name = StringField('Last Name', validators = [InputRequired()])

Sales = db.Table('Sales',
    db.Column('id', db.Integer, primary_key = True, nullable = False),
    db.Column('user_id', db.Integer, db.ForeignKey('Users.id')),
    db.Column('product_id', db.Integer, db.ForeignKey('Products.id')),
    db.Column('sell_date', DateTime(timezone=True), server_default=func.now(), nullable = False)
)
    

class users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column('First Name', db.String(80), nullable = False)
    last_name = db.Column('Last Name', db.String(80), nullable = False)
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

@app.route('/')
def index():
    return 'Hello, welcome to our shop!'

@app.route('/register', methods = ['GET', 'POST'])
def create_user():
    return



