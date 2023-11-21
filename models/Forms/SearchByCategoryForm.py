from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class SearchByCategoryForm(FlaskForm):
    category = StringField('Category')
    submit_search = SubmitField('Search')