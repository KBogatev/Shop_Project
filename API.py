from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import func
from datetime import date
import re
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
    first_name = str(input('Enter your first name:'))
    last_name = str(input('Enter your last name:'))
    if not pattern.match(first_name) or not pattern.match(last_name):
        print("It seems you have made a wrong input.") 
        return "You have encountered an error. Please restart the registration process."
    else:
        new_user = users(first_name=first_name, last_name=last_name)
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

@app.route('/users/unsubscribe', methods = ['GET', 'DELETE'])
def del_user():
    pattern = re.compile(r'[a-zA-Z]')
    try:
        user = int(input("Enter the id of the user you wish to delete:"))
    except ValueError:
        print("Only numbers are accepted.")
    exists = db.session.query(db.exists().where(users.id == user)).scalar()
    if exists == True:
        users.query.filter(users.id == user).delete()
        db.session.commit()    
        return 'User succesfully deleted.'
    else:
        return "It seems that user does not exist in the database."

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

@app.route('/users/update/<id>', methods = ['GET', 'PUT'])
def user_update(id):
    pattern = re.compile(r'[a-zA-Z]')
    user = users.query.filter_by(id = id).first()
    print('What information of the user would you like to update?(1 for first name, 2 for last name.)')
    try:
        updt_choice = int(input('pick one of the options:'))
    except updt_choice > 2 or updt_choice < 1:
        print("That is not one of the options.")
    if updt_choice == 1:
        user.first_name = input('What would you like the new first name of the user to be?:')
        if not pattern.match(user.first_name):
            return "The new first name you have selected is not valid. Please try again."
        else:
            db.session.commit()
            return 'The first name of the user has been updated succesfully.'
    elif updt_choice == 2:
        user.last_name = input('What would you like the new last name of the user to be?:')
        if not pattern.match(user.last_name):
            return "The new last name you have selected is not valid. Please try again."
        else:
            db.session.commit()
            return 'The last name of the user has been updated succesfully.'

@app.route('/items/newitem', methods = ['GET', 'POST'])
def add_item():
    pattern = re.compile(r'[a-zA-Z ]')
    item_name = str(input('Enter the name of your item:'))
    item_desc = str(input('Enter the description of your item:'))
    if not pattern.match(item_name) or not pattern.match(item_desc):
        return "Error! The item you are trying to add is invalid. Please try again."
    else:
        new_item = products(name=item_name, desc=item_desc)
        db.session.add(new_item)
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
    Items = products.query.all()
    itemlist = []

    for item in Items:
        item_data = (f'{item.id}:{item.name} - {item.desc}')
        itemlist.append(item_data)
    print(f"Products: {itemlist}")
    try:
        purchase = int(input("What item do you wish to buy?(Enter the id of the item):"))
        buyer = int(input("Enter the id of the buyer who is purchasing the product:"))
    except ValueError:
        print("Only numbers are accepted.")
    item_exists = db.session.query(db.exists().where(products.id == purchase)).scalar()
    user_exists = db.session.query(db.exists().where(users.id == buyer)).scalar()
    if item_exists == True and user_exists == True:
        new_sale = sales(user_id=buyer, product_id=purchase)
        db.session.add(new_sale)
        return "The item has been succcesfully bought!"
    else:
        return "It seems that either the item being purchased or the user selected do not exist."

@app.route('/items/removeitem', methods = ['GET', 'DELETE'])
def del_item():
    pattern = re.compile(r'[a-zA-Z ]')
    item_name = str(input('Enter the name of the product you wish to delete:'))
    if not pattern.match(item_name):
        return 'Oops! It seems that product does not exist, please try again.'
    else:
        products.query.filter(products.name == item_name).delete()
        db.session.commit()    
        return 'Product succesfully deleted.'

@app.route('/items/update/<id>', methods = ['GET', 'PUT'])
def update_item(id):
    pattern = re.compile(r'[a-zA-Z ]')
    item = products.query.filter_by(id = id).first()
    print('What information of the product would you like to update?(1 for name, 2 for desc, 3 for sell_state)')
    try:
        updt_choice = int(input('pick one of the options:'))
    except updt_choice > 3 or updt_choice < 1:
        print("That is not one of the options.")
    if updt_choice == 1:
        item.name = input('What would you like the new name of the item to be?:')
        if not pattern.match(item.name):
            return "The new item name you have selected is not valid. Please try again."
        else:
            db.session.commit()
            return 'The item name has been succesfully updated.'
    elif updt_choice == 2:
        item.desc = input('What would you like the new description of the item to be?:')
        if not pattern.match(item.desc):
            return "The new item description you have selected is not valid. Please try again."
        else:   
            db.session.commit()
            return 'The item description has been succesfully updated.'
    elif updt_choice == 3:
        if item.sell_state == True:
            item.sell_state = False
            db.session.commit()
            return 'The item is now no longer being sold.'
        else:
            item.sell_state = True
            db.session.commit()
            return 'The item is now up for sale.'
    
    
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

@app.route('/salesinfo', methods = ['GET'])
def sales_info():
    Items = products.query.all()
    itemlist = []
    from_date = date(input("Please select the start date of your query(format: yyyy, m, dd):"))
    to_date = date(input("Please select the end date of your query(format: yyyy, m, dd):"))
    Sales = sales.query.filter(sales.sell_date.between(from_date, to_date)).all()

    for item in Items:
        item_data = (f'{item.name}')
        itemlist.append(item_data)
    return {"Product Sales": itemlist}





    
