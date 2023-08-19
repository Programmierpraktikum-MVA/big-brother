import sys
import os

import numpy as np
import cv2

from face_recognition_strategies.strategies.base_strategy import BaseStrategy
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recog", "ultra_light_and_openface"))
import FaceDetection

class OpenfaceStrategy(BaseStrategy):
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
        try:
            return FaceDetection.authorize_user(data_train, data_test[0])
        except Exception:
            print("openface Algo failed")
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
            float32_im = np.float32(im.astype("uint8"))
            im_RGB = cv2.cvtColor(
                (float32_im / 256).astype("uint8"), 
                cv2.COLOR_BGR2RGB
            )
            processed.append(im_RGB)
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

        data_test = data_test[0]
        processed_data = cv2.resize(
            data_test.astype("uint8"),
            dsize=(maxShape[1], maxShape[0]),
            interpolation=cv2.INTER_CUBIC
        )
        return [processed_data]
