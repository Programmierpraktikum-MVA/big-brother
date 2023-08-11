import os
import logging
from sys import stdout

from flask import Flask
from flask_socketio import SocketIO
import flask_login

from app.websiteSystem import websiteSystem
from config import Config


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

ws = websiteSystem()

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
