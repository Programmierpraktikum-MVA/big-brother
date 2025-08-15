from flask_wtf import FlaskForm
<<<<<<< HEAD
from wtforms import TextField, SubmitField
from wtforms.validators import DataRequired
=======
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Optional
>>>>>>> EduVids-Completing
from flask_wtf.file import FileAllowed, FileField, FileRequired


class VideoUploadForm(FlaskForm):
<<<<<<< HEAD
    name = TextField("Name:", validators=[DataRequired()])
=======
    name = StringField("Name:", validators=[DataRequired()])
>>>>>>> EduVids-Completing
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
<<<<<<< HEAD
    question = TextField("Question:", validators=[DataRequired()])
=======
    question = StringField("Question:", validators=[DataRequired()])
>>>>>>> EduVids-Completing
    submit = SubmitField("Upload")


class QueryForm(FlaskForm):
<<<<<<< HEAD
    query = TextField("Query", validators=[DataRequired()])
=======
    query = StringField("Query", validators=[Optional()])
    file = FileField(
        "Bild oder PDF hochladen:",
        validators=[
            FileAllowed(["png", "jpg", "jpeg", "pdf"], "Nur JPG, PNG oder PDF erlaubt!")
        ]
    )
>>>>>>> EduVids-Completing
    submit = SubmitField("Search")