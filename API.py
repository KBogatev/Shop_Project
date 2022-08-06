from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from datetime import datetime
import re
app = Flask(__name__)
CORS(app)
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
    sell_date = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable = False)
    
class users(db.Model):
    __tablename__ = 'Users'
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column(db.String(80), nullable = False)
    last_name = db.Column(db.String(80), nullable = False)
    joined_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable = False)

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
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable = False)
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
    Users = users.query.count()
    return f'Hello, welcome to our shop! There are currently {Users} registered users.'

@app.route('/users/register', methods = ['GET', 'POST'])
def register():
        pattern = re.compile(r'[a-zA-Z]')
        new_user = users(first_name=request.json['first name'], last_name=request.json['last name'])
        if not pattern.match(str(new_user)):
            return "It seems you have made a wrong input. Please try again."
        db.session.add(new_user)
        db.session.commit()
        return "User registered succesfully!"
@app.route('/users', methods = ['GET'])
def get_users():
    Users = users.query.all()
    userlist = []

    for user in Users:
        user_data = (f'{user.id} - {user.first_name} {user.last_name}')
        userlist.append(user_data)
    return {"Users": userlist}

@app.route('/users/unsubscribe/<id>', methods = ['GET', 'DELETE'])
def del_user(id):
    user = users.query.get(id)
    if user is None:
        return "It seems that user does not exist in the database."
    db.session.delete(user)
    db.session.commit()    
    return 'User succesfully deleted.'

@app.route('/userinfo/<id>', methods = ['GET'])
def user_info(id):
    user = users.query.get(id)
    if user is None:
        return "It seems that user does not exist in the database."
    Sales = sales.query.filter(sales.user_id == id)
    purchase_list = []
    for sale in Sales:
        items = products.query.filter(sale.product_id == products.id).first()
        items_data = (f'{items.name}')
        purchase_list.append(items_data)
    return {f"Purchases of {user.first_name} {user.last_name}" : purchase_list}

@app.route('/users/update/<id>', methods = ['GET', 'PUT'])
def user_update(id):
    user = users.query.filter_by(id = id).first()
    pattern = re.compile(r'[a-zA-Z]')
    user.first_name = request.json['first name']
    user.last_name = request.json['last name']
    if not pattern.match(user.first_name) or not pattern.match(user.last_name):
        return "It seems you have made a wrong input. Please try again."
    db.session.commit()
    return "The user's information has been updated succesfully."

@app.route('/items/newitem', methods = ['GET', 'POST'])
def add_item():
    pattern = re.compile(r'[a-zA-Z]')
    item = products(name = request.json['item name'], desc = request.json['description'])
    if not pattern.match(str(item)):
            return "It seems you have made a wrong input. Please try again."
    db.session.add(item)
    db.session.commit()
    return 'Product added succesfully!'

@app.route('/items', methods = ['GET'])
def get_items():
    Items = products.query.all()
    itemlist = []
    for item in Items:
        item_data = (f'{item.id}:{item.name} - {item.desc}')
        itemlist.append(item_data)
    return {"Products": itemlist}

@app.route('/items/buy', methods = ['GET', 'POST'])
def buy_item():
        userlist = []
        itemlist = []
        Users = users.query.all()
        Items = products.query.all()
        for user in Users:
            userlist.append(user.id)
        for item in Items:
            itemlist.append(item.id)
        new_sale = sales(user_id = request.json['user id'], product_id = request.json['product id'])
        exists1 = db.session.query(db.exists().where(users.id == new_sale.user_id)).scalar()
        exists2 = db.session.query(db.exists().where(products.id == new_sale.product_id)).scalar()
        if exists1 == True and exists2 == True:
            db.session.add(new_sale)
            db.session.commit()
            return "The item has been succcesfully bought!"
        else:
            return "It seems you have made a wrong input. Please try again."

@app.route('/items/featured', methods = ['GET'])
def featured_item():
    Sales = sales.query.all()
    Items = products.query.all()
    itemlist = []
    SaleCount = 0
    def myFunc(e):
        return e['Sales']

    for item in Items:
        SaleCount = 0
        for sale in Sales:
            if sale.product_id == item.id:
                SaleCount = SaleCount + 1
        item_data = {'item': item.name, 'Sales': SaleCount}
        itemlist.append(item_data)  
    itemlist.sort(reverse = True, key=myFunc)
    return {"Most popular items.": itemlist}

@app.route('/items/removeitem/<id>', methods = ['GET', 'DELETE'])
def del_item(id):
    item = products.query.get(id)
    if item is None:
        return "It seems that product does not exist in the database."
    db.session.delete(item)
    db.session.commit()
    return 'Product succesfully deleted.'

@app.route('/items/update/<id>', methods = ['GET', 'PUT'])
def update_item(id):
    item = products.query.filter_by(id = id).first()
    pattern = re.compile(r'[a-zA-Z]')
    item.name = request.json['item name']
    item.desc = request.json['description']
    item.sell_state = request.json['sell state']
    if not pattern.match(item.name) or not pattern.match(item.desc) or not pattern.match(item.sell_state):
        return "It seems you have made a wrong input. Please try again."
    db.session.commit()
    return "The product's information has been updated succesfully."
    
    
@app.route('/iteminfo/<id>', methods = ['GET'])
def item_info(id):
    item = products.query.get(id)
    if item is None:
        return "It seems that product does not exist in the database."
    Sales = sales.query.filter(sales.product_id == id)
    salelist = []
    for sale in Sales:
        buyer = users.query.filter(sale.user_id == users.id).first()
        buyer_data = (f'{buyer.first_name} {buyer.last_name}')
        salelist.append(buyer_data)
    return {f"Buyers of {item.name}" : salelist}

@app.route('/salesinfo', methods = ['GET', 'POST'])
def sales_info():
    Items = products.query.all()
    itemlist = []
    SaleCount = 0
    try:
        start_date = datetime.strptime(request.json['start date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.json['end date'], '%Y-%m-%d')
    except ValueError:
        return "The dates you provided were invalid."
    Sales = sales.query.filter(sales.sell_date.between(start_date, end_date)).all()

    for item in Items:
        SaleCount = 0
        for sale in Sales:
            if sale.product_id == item.id:
                SaleCount = SaleCount + 1
        item_data = (f"{item.name}:{SaleCount}")
        itemlist.append(item_data)  

    return {"Sales Info": itemlist}






    
