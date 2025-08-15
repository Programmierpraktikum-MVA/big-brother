import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
<<<<<<< HEAD
=======
    TEMPLATES_AUTO_RELOAD = True
>>>>>>> EduVids-Completing
