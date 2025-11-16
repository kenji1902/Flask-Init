from flask import url_for


def about():
    # Example usage of blueprint static files
    css_url = url_for('about.static', filename='about.css')
    return f"<link rel=\"stylesheet\" href=\"{css_url}\">\n<h1>About page</h1>"
