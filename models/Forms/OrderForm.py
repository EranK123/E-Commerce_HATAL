from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class OrderForm(FlaskForm):
    submit = SubmitField('Order')
