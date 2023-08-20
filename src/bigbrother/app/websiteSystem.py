import os
import sys
import time
import queue
import uuid
import typing


import numpy as np
import cv2


from app.user import BigBrotherUser

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "haar_and_lbph"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "wire_face_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "ultra_light_and_openface"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "DBM"))

import FaceDetection
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
from face_rec_main import train_add_faces, authorize_faces
from cv2RecogClass import cv2Recog

from face_recognition_strategies.context import FaceRecognitionContext
from face_recognition_strategies.strategies.cv2_strategy import Cv2Strategy
from face_recognition_strategies.strategies.openface_strategy import OpenfaceStrategy
from face_recognition_strategies.strategies.principle_component_analysis_strategy import PCAStrategy

import DatabaseManagement as DBM


# TODO: Make this conform with the naming convention.
# TODO: Rename it as user management
class websiteSystem:
    def __init__(self):
        self.DB = DBM.wire_DB()

        # Keeps track of the users and their session keys
        self.BigBrotherUserList = []
        userDict = self.DB.getUsers().items()
        for key, value in self.DB.getUsers().items():
            self.BigBrotherUserList.append(BigBrotherUser(key, value, self.DB))

    # TODO: Reimplement this for more efficient and correct searching
    def get_user_by_id(self, user_uuid: uuid.UUID) -> typing.Optional[BigBrotherUser]:
        """
        Searches and returns the a user with a certain id.

        Arguments:
        user_uuid -- The ID of the user that you are trying to search.

        Return:
        Returns the user with the give ID. Returns None if the user
        with the ID doesn't exist.

        Exception:
        TypeError -- Gets risen if the type of the arguments is incorrect.
        """
        if type(user_uuid) != uuid.UUID:
            raise TypeError

        # TODO: Implement a more efficient way of searching
        for user in self.BigBrotherUserList:
            if user.uuid == user_uuid:
                return user
        return None

    # TODO: Doesn't really belong here. As far as I understand this class is
    # made for user management regarding the DB and authenticating the
    # picture is for logic. This should be a part of the utility package
    # in the login section.
    def authenticatePicture(self, user, pic, cookie):
        """
        We assume that the user with the given uuid already exists
        """
        # TODO: Cookie is not necessary
        # TODO: expect a user_uuid instead of an ID
        user_uuid = user["uuid"]
        username = self.DB.getUserWithId(user_uuid)
        training_data, _ = self.DB.getTrainingPictures(user_uuid=user_uuid)

        face_recognition_context = FaceRecognitionContext(Cv2Strategy())

        face_recognition_context.set_strategy(Cv2Strategy())
        cv_result = face_recognition_context.execute_strategy(
            training_data, pic
        )

        face_recognition_context.set_strategy(OpenfaceStrategy())
        openface_result = face_recognition_context.execute_strategy(
            training_data, pic
        )

        face_recognition_context.set_strategy(PCAStrategy(user_uuid))
        pca_result = face_recognition_context.execute_strategy(
            training_data, pic
        )

        # algorithm is weighted
        algoScore = int(cv_result) * 60 + int(openface_result) * 20 + int(pca_result) * 20

        # TODO: Why has 40 been chosen?
        # The authentication algorithm should only to one thing 
        # -> authenticate the pictures. They shouldn't insert things into the database.
        if algoScore >= 40:
            # TODO: Transform image before inserting them into the database.
            return self.DB.insertTrainingPicture(pic, user_uuid)
        else:
            return False
