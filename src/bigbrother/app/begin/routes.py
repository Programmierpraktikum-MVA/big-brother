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
from flask import Blueprint
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

main = Blueprint('main', __name__)

@main.route("/team")
def team():
    return render_template("team.html")

@main.route("/team2")
def team2():
    return render_template("team_23.html")

@main.route("/algorithms")
def algorithms():
    return render_template("algorithms.html")

@main.route('/index', methods=['GET', 'POST'])
@main.route('/',methods=['GET', 'POST'])
def index():
    form = None
    if request.method == 'POST':
        return logincamera()

    cookie = request.cookies.get('session_uuid')
    if not cookie:

        response = make_response(render_template('index.html', BigBrotherUserList = ws.BigBrotherUserList,form = form))
        uuid_ = uuid.uuid4()
        print("setting new uuid: ",uuid_)
        response.set_cookie('session_uuid', str(uuid_))


        return response
    return render_template('index.html', BigBrotherUserList = ws.BigBrotherUserList,form = form)
