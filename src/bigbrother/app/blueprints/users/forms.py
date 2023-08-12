from wtforms import Form, TextField, SubmitField, FileField
from wtforms.validators import DataRequired


class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


class SignUpForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic1 = FileField('Picture:', validators=[DataRequired()])
    pic2 = FileField('Picture:', validators=[DataRequired()])
    pic3 = FileField('Picture:', validators=[DataRequired()])
    submit = SubmitField('Sign Up')
