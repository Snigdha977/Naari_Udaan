from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///naari_udaan.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key

# Initialize SQLAlchemy
db = SQLAlchemy(app)