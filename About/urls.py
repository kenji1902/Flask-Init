from flask import Blueprint
from About.views import about

# Blueprint for About app
about_bp = Blueprint(
    'about',
    __name__,
    static_folder='static',
    static_url_path='/about_static',
    template_folder='templates'
)

# Register routes using add_url_rule
about_bp.add_url_rule('/about/', 'about', about, methods=['GET'])
