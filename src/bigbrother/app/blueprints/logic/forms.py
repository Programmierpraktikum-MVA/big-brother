from wtforms import Form, TextField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField


class VideoUploadForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    video = FileField(
        'Video:',
        validators=[
            DataRequired(),
            FileAllowed(['.mp4'], 'MP4 Videos only!')
        ]
    )
    submit = SubmitField('Upload')


class CameraForm(Form):
    name = TextField('Name:', validators=[DataRequired()])
    submit = SubmitField('Sign In')


# TODO: Basically the same as VideoUploadForm, discuss whether this is
# still needed! We should probably delete this and use VideoUploadForm
# instead.
class EduVidForm(Form):
    eduName = TextField('Name', validators=[DataRequired()])
    eduVid = FileField(
        'Video',
        # TODO: Should be deleted
        validators=[
            DataRequired(),
            FileAllowed(['.mp4'], 'MP4 Videos only!')
        ]
    )
    submit = SubmitField('Upload')
