from flask_wtf import FlaskForm
from wtforms import Form, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class NameForm(FlaskForm):
    name = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')

