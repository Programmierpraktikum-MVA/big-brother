import sys
import os

import numpy as np

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "face_recog", "haar_and_lbph"))
from cv2RecogClass import cv2Recog

class Cv2Strategy(BaseStrategy):
    def execute(self, data_train, data_test):
        """
        Executes the cv2 strategy.

        Arguments:
        data_train -- List of images to train with.
        data_test -- List with a single test image.

        Return:
        Returns True if the test data matches with the training data and False
        otherwise.
        """
        if len(data_test) != 1:
            return False

        recognizer = cv2Recog()
        temp_id = 22  # random temporary id
        recognizer.train_add_faces(temp_id, data_train, save_model=False)

        testDists = np.zeros(len(imgs_train))
        try:
            for train_index, train_im in enumerate(data_train):
                dist[train_index] = recognizer.dist_between_two_pics(train_im, data_test[0])
            dists = np.min(dist)
            return dists < 125
        except cv2.error:
            print("cv2 Algo failed!")
            return False

    def preprocess_training_data(self, data_train):
        maxShape = (0, 0)
        for im in data_train:
            if im.shape[0]*im.shape[1] > maxShape[0]*maxShape[1]:
                maxShape = im.shape

        processed = []
        for im in data_train:
            im = cv2.resize(
                im.astype("uint8"),
                dsize=(maxShape[1], maxShape[0]),
                interpolation=cv2.INTER_CUBIC
            )
            norm_im = cv2.normalize(
                src=im.astype("uint8"), dst=None,
                alpha=0, beta=255,
                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
            )
            processed.append(norm_im)

        return processed

    def preprocess_testing_data(self, data_test):
        """
        Arguments:
        data_test --

        Return:
        Returns list of processed testing data. Since this algorithm only
        accepts one data a list of length one will be returned

        Exception:
        RuntimeError -- If data_test has more or less than one element.
        """
        if len(data_test) != 1:
            raise RuntimeError("This algorithm only expects exactly one test data.")

        data_test = data_test[0]
        processed_data = cv2.resize(
            data_test.astype("uint8"),
            dsize=(maxShape[1], maxShape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        processed_data = cv2.normalize(
            src=processed_data.astype("uint8"), dst=None,
            alpha=0, beta=255,
            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )

        return [processed_data]
