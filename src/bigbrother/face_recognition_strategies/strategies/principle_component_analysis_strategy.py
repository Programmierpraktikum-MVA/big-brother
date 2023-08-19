import sys
import os

import numpy as np
import cv2

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "wire_face_recognition"))
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "DBM"))
import DatabaseManagement as DBM

class OpenfaceStrategy(BaseStrategy):
    def __init__(self, user_uuid):
        self.DB = DBM.wire_DB()
        self.set_user_uuid(user_uuid)
        self.username = self.DB.getUserWithId(user_uuid)

        self.maxShape = (0,0)

    def set_user_uuid(self, user_uuid):
        if type(user_uuid) == uuid.UUID:
            self.user_uuid = user_uuid
        else:
            raise ValueError

    def execute(self, data_train, data_test):
        """
        Executes the openface strategy.

        Arguments:
        data_train -- List of images to train with.
        data_test -- List with a single test image.

        Return:
        Returns True if the test data matches with the training data and False
        otherwise.
        """
        if len(data_test) != 1:
            return False
        recog_usernames = recogFace([pic, self.user_uuid])
        wireMatch = username in recog_usernames

    def preprocess_training_data(self, data_train):
        maxShape = (0, 0)
        for im in data_train:
            if im.shape[0]*im.shape[1] > maxShape[0]*maxShape[1]:
                maxShape = im.shape
        return processed

    def preprocess_testing_data(self, data_test):
        """
        Arguments:
        data_test -- List of length one containing data to test.

        Return:
        Returns list of processed testing data. Since this algorithm only
        accepts one data a list of length one will be returned

        Exception:
        RuntimeError -- If data_test has more or less than one element.
        """
        if len(data_test) != 1:
            raise RuntimeError("This algorithm only expects exactly one test data.")

        maxShape = (0, 0)
        for im in data_train:
            if im.shape[0]*im.shape[1] > maxShape[0]*maxShape[1]:
                maxShape = im.shape

        data_test = data_test[0]
        processed_data = cv2.resize(
            data_test.astype("uint8"),
            dsize=(maxShape[1], maxShape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        return [processed_data]
