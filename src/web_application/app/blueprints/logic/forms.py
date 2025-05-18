from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf.file import FileAllowed, FileField, FileRequired


class VideoUploadForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    video = FileField(
        "Video:",
        validators=[
            FileRequired(),
            FileAllowed(["mp4"])
        ])
    segments = FileField(
        "Time-Stamps:",
        validators=[
            DataRequired(),
            FileAllowed(["json"])
        ])
    question = StringField("Question:", validators=[DataRequired()])
    submit = SubmitField("Upload")


class QueryForm(FlaskForm):
    query = StringField("Query", validators=[DataRequired()])
    submit = SubmitField("Search")