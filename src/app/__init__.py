import os
from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__)

    # Load configuration from the config directory
    app.config.from_pyfile('../../config/config.py')

    # Initialize MongoDB
    mongo.init_app(app)

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app