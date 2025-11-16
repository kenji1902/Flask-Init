from flask import Flask
from MainApp.settings.base import base
from MainApp.db import db,migrate


def create_app(config_class=base):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database with the app
    db.init_app(app)
    migrate.init_app(app, db)
    # Register blueprints from central registry
    from MainApp.blueprints import register_blueprints
    register_blueprints(app)
    
    return app
