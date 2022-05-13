from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, DateTime
from sqlalchemy.sql import func

app = Flask(__name__)
url = "mysql://root:root@localhost:52631"
engine = create_engine(url)
create_str = "CREATE DATABASE IF NOT EXISTS shop_db;"
engine.execute(create_str)
engine.execute("USE shop_db;")
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost:52631/shop_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
@app.route('/')
def index():
    return 'Hello!'


class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True, nullable = False)
    first_name = db.Column(db.String(80), nullable = False)
    last_name = db.Column(db.String(80))
    joined_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True, nullable = False)
    name = db.Column(db.String(100), nullable = False)
    created_at = db.Column(DateTime(timezone=True), server_default=func.now(), nullable = False)
    sell_state = db.Column(db.Boolean)

db.create_all()
db.session.commit()
