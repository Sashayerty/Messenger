from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class FriendsForm(FlaskForm):
    name_of_user = StringField(validators=[DataRequired()])
    search = SubmitField('Search')