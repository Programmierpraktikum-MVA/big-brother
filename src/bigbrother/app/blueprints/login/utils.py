import os
import sys
import uuid

import numpy as np

from face_recognition_strategies.context import FaceRecognitionContext
from face_recognition_strategies.strategies.cv2_strategy import Cv2Strategy
from face_recognition_strategies.strategies.openface_strategy import OpenfaceStrategy
from face_recognition_strategies.strategies.principle_component_analysis_strategy import PCAStrategy

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "DBM"))
import DatabaseManagement as DBM

def authenticate_picture(user_uuid: uuid.UUID, picture: np.ndarray):
    """
    Authenticates picture from a certain user

    We assume that the user with the given uuid already exists
    """
    DB = DBM.wire_DB()
    username = DB.getUserWithId(user_uuid)
    training_data, _ = DB.getTrainingPictures(user_uuid=user_uuid)

    face_recognition_context = FaceRecognitionContext(Cv2Strategy())

    face_recognition_context.set_strategy(Cv2Strategy())
    cv_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    face_recognition_context.set_strategy(OpenfaceStrategy())
    openface_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    face_recognition_context.set_strategy(PCAStrategy(user_uuid))
    pca_result = face_recognition_context.execute_strategy(
        training_data, picture
    )

    # algorithm is weighted
    algo_score = int(cv_result) * 60 + int(openface_result) * 20 + int(pca_result) * 20

    # TODO: Why has 40 been chosen?
    # The authentication algorithm should only to one thing 
    # -> authenticate the pictures. They shouldn't insert things into the database.
    THRESHHOLD_FOR_WEIGHTED_SCORE = 40
    if algo_score >= THRESHHOLD_FOR_WEIGHTED_SCORE:
        # TODO: Transform image before inserting them into the database.
        return DB.insertTrainingPicture(picture, user_uuid)
    else:
        return False
