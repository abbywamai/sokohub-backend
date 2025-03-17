from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:wamai@localhost/sokohub"
db = SQLAlchemy(app)

if __name__ == "__main__":
    app.run()