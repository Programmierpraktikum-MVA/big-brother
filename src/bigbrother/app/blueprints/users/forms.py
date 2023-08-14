from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, FileField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class CameraForm(FlaskForm):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignUpForm(FlaskForm):
    name = TextField('Name:', validators=[DataRequired()])
    pic1 = FileField('Picture:', validators=[DataRequired()])
    pic2 = FileField('Picture:', validators=[DataRequired()])
    pic3 = FileField('Picture:', validators=[DataRequired()])
    submit = SubmitField('Sign Up')
