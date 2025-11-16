from flask import url_for


def index():
    css_url = url_for('home.static', filename='home.css')
    return f"<link rel=\"stylesheet\" href=\"{css_url}\">\n<h1>Home page</h1>"
