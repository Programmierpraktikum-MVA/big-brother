from flask_wtf import FlaskForm
from wtforms import Form, TextField, TextAreaField,StringField, SubmitField, FileField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired
from werkzeug.utils import secure_filename

class SignUpForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic1 = FileField('Picture:')
    pic2 = FileField('Picture:')
    pic3 = FileField('Picture:')
    submit = SubmitField('Sign Up')


class SignInForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    pic = FileField('Picture:')
    submit = SubmitField('Sign In')


class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')
    

class VideoUploadForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    video = FileField(
            'Video:', 
            validators=[
                DataRequired(),
                FileAllowed(['.mp4'], 'MP4 Videos only!')
            ]
        )
    submit = SubmitField('Hochladen')
    

#kim: eigentlich müll diese drei forms
class CreateForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    picturefront = FileField(
            'Gesicht von vorne', 
             validators=[
                 FileRequired(), 
                 FileAllowed(['jpg', 'png'], 'PNG Images only!')
             ]
         )
    pictureleft = FileField(
            'Gesicht von links', 
            validators=[
                FileRequired(), 
                FileAllowed(['jpg','png'], 'PNG Images only!')
            ]
        )
    pictureright = FileField(
            'Gesicht von rechts', 
            validators=[
                FileRequired(),
                FileAllowed(['jpg','png'], 'PNG Images only!')
            ]
        )
    submit = SubmitField('Sign In')


class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    # Added File Required and FileAllowed to Field
    picture = FileField(
            'Gesicht von vorne', 
            validators=[
                FileRequired(),
                FileAllowed(['jpg','png'], 'PNG Images only!')
            ]
        )
    submit = SubmitField('Sign In')


class LoginCameraForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    # Added File Required and FileAllowed to Field
    submit = SubmitField('Sign In')
