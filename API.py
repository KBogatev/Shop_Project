from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

@app.route('/'):
def index():
    return 'Hello!'