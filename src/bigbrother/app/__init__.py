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

# Own libraries
## Tells python where to search for modules
sys.path.append(os.path.join(os.path.dirname(__file__),".."))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','WiReTest'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition','haar_and_lbph'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','FaceRecognition'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','DBM'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..','..','Logik'))

from config import Config

## Databse and website management
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

# This has to be at the bottom in order to avoid cyclic dependencies
from app.begin.routes import main
from app.logic.routes import logic
from app.users.routes import users
from app.login.routes import blueprint_login

application.register_blueprint(main)
application.register_blueprint(logic)
application.register_blueprint(users)
application.register_blueprint(blueprint_login)

