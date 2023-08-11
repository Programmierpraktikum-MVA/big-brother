from flask_wtf import FlaskForm
from wtforms import Form, TextField, TextAreaField,StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.utils import secure_filename

class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    submit = SubmitField('Sign In')

class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class SignUpForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic1 = FileField('Picture:')
    pic2 = FileField('Picture:')
    pic3 = FileField('Picture:')
    submit = SubmitField('Sign Up')
