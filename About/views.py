from flask import url_for, render_template
from About.model.about import about as AboutModel
from datetime import datetime


def about():
    """View for the About page.

    Each time the page is viewed we create and save an About model record
    containing the view timestamp in the content field, then render the
    template showing that content.
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    content_text = f'viewed at '

    # Persist a record to the DB (committed immediately)
    record = AboutModel(content=content_text)
    record.save(commit=True)

    # Query all records to display history (most recent first)
    entries = AboutModel.query.order_by(AboutModel.id.desc()).all()

    # Render the template and include the css url and entries
    css_url = url_for('about.static', filename='about.css')
    return render_template('about.html', css_url=css_url, entries=entries)
