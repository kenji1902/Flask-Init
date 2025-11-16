
from flask import Blueprint
from MainApp.views import index, about
# Create a blueprint for your routes
main = Blueprint("main", __name__)

