from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, DateTime
from sqlalchemy.sql import func

app = Flask(__name__)
url = "mysql://root:root@localhost:50785"
engine = create_engine(url)
create_str = "CREATE DATABASE IF NOT EXISTS shop_db;"
engine.execute(create_str)
engine.execute("USE shop_db;")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:50785/shop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column('First Name', db.String(80), nullable = False)
    last_name = db.Column('Last Name', db.String(80), nullable = False)
    joined_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)

class products(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column('Name', db.String(100), nullable = False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    sell_state = db.Column(db.Boolean, nullable = False)

class sales(db.Model):
    __tablename__ = 'Sales'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    user_id = db.Column('user_id', db.Integer, db.ForeignKey('Users.id'))
    product_id = db.Column('product_id', db.Integer, db.ForeignKey('Products.id'))
    sell_date = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    user = db.relationship('Users', backref=db.backref('sales'))
    product = db.relationship('Products', backref=db.backref('sales'))

db.create_all()
db.session.commit()

