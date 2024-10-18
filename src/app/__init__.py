import os
from flask import Flask
from flask_pymongo import PyMongo

mongo = PyMongo()

def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")

    # Define the path to the config file dynamically
    config_path = os.path.join(os.path.dirname(__file__), '../../config/config.py')
    app.config.from_pyfile(config_path)

    # Initialize MongoDB
    mongo.init_app(app)

    # Register routes
    from .routes import main
    app.register_blueprint(main)

    return app
