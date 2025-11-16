from flask import Blueprint
from Home.views import index

# Blueprint for Home app
home_bp = Blueprint(
    'home',
    __name__,
    static_folder='static',
    static_url_path='/home_static',
    template_folder='templates'
)

# Register routes using add_url_rule
home_bp.add_url_rule('/', 'index', index, methods=['GET'])
