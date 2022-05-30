from flask import Flask, request, url_for, redirect
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

class sales(db.Model):
    __tablename__ = 'Sales'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Products.id'))
    sell_date = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    
class users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column(db.String(80), nullable = False)
    last_name = db.Column(db.String(80), nullable = False)
    joined_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
        
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

class products(db.Model):
    __tablename__ = 'Products'
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column('Name', db.String(100), nullable = False, unique = True)
    desc = db.Column('Description', db.String(255), nullable = False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    sell_state = db.Column(db.Boolean, default = True, nullable = False)

    def __repr__(self):
        return f'Product:{self.name} - {self.desc}'
    
    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

db.create_all()
db.session.commit()

@app.route('/')
def index():
    return 'Hello, welcome to our shop!'

@app.route('/users/register', methods = ['GET', 'POST'])
def register():
    first_name = str(input('Enter your first name:'))
    last_name = str(input('Enter your last name:'))
    new_user = users(first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()
    return 'User registered succesfully!'


@app.route('/users', methods = ['GET'])
def get_users():
    Users = users.query.all()
    userlist = []

    for user in Users:
        user_data = (f'{user.first_name} {user.last_name}')
        userlist.append(user_data)
    return {"Users": userlist}

@app.route('/users/unsubscribe', methods = ['GET', 'DELETE'])
def del_user():
    try:
        first_name = str(input('Enter the first name of the user you wish to delete:'))
        last_name = str(input('Enter the last name of the user you wish to delete:'))
        users.query.filter(users.first_name == first_name, users.last_name==last_name).delete()
        db.session.commit()    
    except ValueError:
        return 'Oops! It seems that user does not exist, please try again.'
    return 'User succesfully deleted.'

@app.route('/userinfo/<id>', methods = ['GET'])
def user_info(id):
    user = users.query.get(id)
    Sales = sales.query.filter(sales.user_id == id)
    purchase_list = []
    for sale in Sales:
        items = products.query.filter(sale.product_id == products.id).first()
        items_data = (f'{items.name}')
        purchase_list.append(items_data)
    return {f"Purchases of {user.first_name} {user.last_name}" : purchase_list}
@app.route('/items/newitem', methods = ['GET', 'POST'])
def add_item():
    item_name = str(input('Enter the name of your item:'))
    item_desc = str(input('Enter the description of your item:'))
    new_item = products(name=item_name, desc=item_desc)
    db.session.add(new_item)
    db.session.commit()
    return 'Product added succesfully!'

@app.route('/items', methods = ['GET'])
def get_items():
    Items = products.query.all()
    itemlist = []

    for item in Items:
        item_data = (f'{item.name} - {item.desc}')
        itemlist.append(item_data)
    return {"Products": itemlist}

@app.route('/items/removeitem', methods = ['GET', 'DELETE'])
def del_item():
    try:
        item_name = str(input('Enter the name of the product you wish to delete:'))
        products.query.filter(products.name == item_name).delete()
        db.session.commit()    
    except ValueError:
        return 'Oops! It seems that product does not exist, please try again.'
    return 'Product succesfully deleted.'

@app.route('/iteminfo/<id>', methods = ['GET'])
def item_info(id):
    item = products.query.get(id)
    Sales = sales.query.filter(sales.product_id == id)
    salelist = []
    for sale in Sales:
        buyer = users.query.filter(sale.user_id == users.id).first()
        buyer_data = (f'{buyer.first_name} {buyer.last_name}')
        salelist.append(buyer_data)
    return {f"Buyers of {item.name}" : salelist}





    
