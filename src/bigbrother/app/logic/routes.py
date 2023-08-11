# Standard libraries
import os
import sys


# Third party
from flask import render_template, request, Blueprint
import flask_login

import cv2
import cv2.misc

# Own libraries
# Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'Logik'))

# GUI and frontend libraries
from app.logic.forms import VideoUploadForm, CameraForm

# ML libraries
import Gesture_Recognition.GestureReco_class as GestureRec


logic = Blueprint("logic", __name__)


@logic.route("/gestureReco", methods=["GET", "POST"])
def gestureReco():
    form = CameraForm(request.form)

    rejectionDict = {
        "reason": "Unknown",
        "redirect": "login",
        "redirectPretty": "Back to login",
    }

    if request.method == "GET":
        return render_template("gestureReco.html", form=form)

    if request.method == 'POST' and form.validate():

        capture = cv2.VideoCapture(0)
        gesture = GestureRec.GestureReco()

        while True:
            _, frame = capture.read()
            frame, className = gesture.read_each_frame_from_webcam(frame)
            cv2.putText(frame, className, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

            # Show the final output
            cv2.imshow("Output", frame)

            if cv2.waitKey(1) == ord('q'):
                break

        capture.release()
        cv2.destroyAllWindows()

        return render_template('gestureRecoJS.html', title='Camera')

    return render_template("rejection.html", rejectionDict=rejectionDict)


@logic.route("/eduVid", methods=["GET", "POST"])
@flask_login.login_required
def eduVid():
    form = VideoUploadForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            video = form.video.data

            # TODO: EduVid Implementation

        return "Video has been successfully uploaded!"
    return render_template("eduVid.html", form=form)
