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
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','WiReTest'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition','haar_and_lbph'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','Logik'))

## GUI and frontend libraries
from app.user import BigBrotherUser
from app.forms import SignUpForm, SignInForm, CameraForm, VideoUploadForm, \
                      LoginForm, CreateForm, LoginCameraForm
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


print("Starting BigBrother")

application = Flask(__name__)
application.config.from_object(Config)

application.logger.addHandler(logging.StreamHandler(stdout))
application.config['SECRET_KEY'] = 'secret!'
application.config['DEBUG'] = True
application.config['UPLOAD_FOLDER'] = application.instance_path
application.config['LOCALDEBUG'] = None

login_manager = flask_login.LoginManager()
login_manager.init_app(application)

ws = websiteSystem.websiteSystem()

if os.environ.get('LOCALDEBUG') == "True":
    application.config['LOCALDEBUG'] = True
else:
    application.config['LOCALDEBUG'] = False
socketio = SocketIO(application)

# has to be put at the bottom
from app import routes
