from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True

# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogs:moopoo@localhost:8889/blogs'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
# Secret keys should not be out here. But for simplicity it will stay.
app.secret_key = 'z143kGgms!zP3C'
