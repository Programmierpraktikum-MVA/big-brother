from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class SignInForm(FlaskForm):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    submit = SubmitField('Sign In')


class CameraForm(FlaskForm):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')
