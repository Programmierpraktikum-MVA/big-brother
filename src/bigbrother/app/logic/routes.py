# Standard libraries
## OS services
import os
import io
import time
import logging

## Runtime services
from sys import stdout
import sys
import traceback

## Misc
import random
import base64
import copy
import ssl
import uuid
import pickle

## Concurrent execution
import multiprocessing as mp
import queue


# Third party
## Flask
from flask import Flask, Response, render_template, request, session, \
                  make_response, flash, redirect, url_for
from flask_socketio import SocketIO, emit
import flask_login
from flask import Blueprint

## Math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib as mpl

## Dealing with images
from imageio import imread
from PIL import Image
import cv2
import cv2.misc

## Misc
from werkzeug.utils import secure_filename
import click

# Own libraries
## Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','..','WiReTest'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','..','FaceRecognition','haar_and_lbph'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','..','FaceRecognition'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','..','DBM'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..','..','Logik'))

## GUI and frontend libraries
from app import application, socketio, login_manager, ws
from app.user import BigBrotherUser
from app.logic.forms import VideoUploadForm, CameraForm
from app.utils import base64_to_pil_image, pil_image_to_base64
from config import Config

## ML libraries
import FaceDetection
import face_recognition
import Face_Recognition.FaceReco_class as LogikFaceRec
import Gesture_Recognition.GestureReco_class as GestureRec

## Databse and website management
import DatabaseManagement as DBM
import websiteSystem


logic = Blueprint("logic", __name__)

@logic.route("/gestureReco", methods=["GET","POST"])
def gestureReco():
    form = CameraForm(request.form)

    rejectionDict = {
            "reason" : "Unknown",
            "redirect" : "login",
            "redirectPretty" : "Back to login",
        }

    if request.method == 'GET':
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

@logic.route("/eduVid", methods=['GET','POST'])
@flask_login.login_required
def eduVid():
    form = VideoUploadForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            video = form.video.data
            
            #TODO: EduVid Implementation
            
            
        return 'Das Video wurde erfolgreich hochgeladen.'  
    return render_template("eduVid.html", form=form)
