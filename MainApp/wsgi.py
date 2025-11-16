import os
from importlib import import_module
from MainApp.app import create_app

# Get config name from environment, default to 'base'
config_name = os.environ.get('FLASK_CONFIG', 'base')

# Dynamically import the config class
try:
    config_module = import_module(f'MainApp.settings.{config_name}')
    config_class = getattr(config_module, config_name)
except (ImportError, AttributeError):
    raise ValueError(f"Config '{config_name}' not found in settings folder")

app = create_app(config_class)
