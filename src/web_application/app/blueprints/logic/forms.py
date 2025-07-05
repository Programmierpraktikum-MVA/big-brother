from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
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
    query = StringField("Query", validators=[Optional()])
    file = FileField(
        "Bild oder PDF hochladen:",
        validators=[
            FileAllowed(["png", "jpg", "jpeg", "pdf"], "Nur JPG, PNG oder PDF erlaubt!")
        ]
    )
    submit = SubmitField("Search")