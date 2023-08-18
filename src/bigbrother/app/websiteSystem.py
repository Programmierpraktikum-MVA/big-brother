import os
import sys
import time
import queue
import uuid
import typing


import numpy as np
import cv2


from app.user import BigBrotherUser

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recognition", "haar_and_lbph"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recognition", "wire_face_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recognition", "ultra_light_and_openface"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "face_recognition"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "DBM"))

import FaceDetection
from wireUtils import load_images as load_test_imgs
from modifiedFaceRecog import recogFace
from face_rec_main import train_add_faces, authorize_faces
from cv2RecogClass import cv2Recog

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

        # prepare the training images
        imgs_raw, uuids = self.DB.getTrainingPictures(user_uuid=user_uuid)
        maxShape = (0, 0)
        for im in imgs_raw:
            if im.shape[0]*im.shape[1] > maxShape[0]*maxShape[1]:
                maxShape = im.shape

        imgs_train = []
        resized_imgs = []
        for im in imgs_raw:
            im = cv2.resize(
                im.astype("uint8"),
                dsize=(maxShape[1], maxShape[0]),
                interpolation=cv2.INTER_CUBIC
            )
            
            # Normalized images (used for cv2 algorithms)
            norm_im = cv2.normalize(
                src=im.astype("uint8"), dst=None,
                alpha=0, beta=255,
                norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
            )
            imgs_train.append(norm_im)

            # only resized images (used for openface algorithms)
            float32_im = np.float32(im.astype("uint8"))
            im_RGB = cv2.cvtColor((float32_im / 256).astype("uint8"), cv2.COLOR_BGR2RGB)
            resized_imgs.append(im_RGB)

        ######################## cv2 algorithm ##################################

        # use temporary integer ID to train a completely new model and check if it 
        # recognized the same person in authorisation login picture
        cv2Inst = cv2Recog()
        temp_ID = 22
        cv2Inst.train_add_faces(temp_ID, imgs_train, save_model=False)

        # Authorize: check if the training pitures are the same person as the given login picture
        cv_result, dists = False, None
        pic = cv2.resize(
            pic.astype("uint8"),
            dsize=(maxShape[1], maxShape[0]),
            interpolation=cv2.INTER_CUBIC
        )

        cv_test_img = cv2.normalize(
            src=pic.astype("uint8"), dst=None,
            alpha=0, beta=255,
            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
        )
        testDists = np.zeros(len(imgs_train))
        try:
            for train_im_index, train_im in enumerate(imgs_train):
                testDists[train_im_index] = cv2Inst.dist_between_two_pics(train_im, cv_test_img)
            dists = np.min(testDists)
            cv_result = dists < 125
        except cv2.error:
            print("cv2 Algo failed!")

        ####################### openface algorithm #########################
        openface_result = False
        try:
            openface_result = FaceDetection.authorize_user(resized_imgs, pic)
        except Exception:
            print("openface Algo failed")

        ################### wire algorithm ############################
        recogUsernames = recogFace([pic, user_uuid])
        print(recogUsernames)
        wireMatch = username in recogUsernames


        ################### evaluate algorithms ############################

        # algorithm is weighted
        algoScore = int(cv_result) * 60 + int(openface_result) * 20 + int(wireMatch) * 20

        # TODO: Why has 40 been chosen?
        # The authentication algorithm should only to one thing -> authenticate
        # the pictures. They shouldn't insert things into the database.
        if algoScore >= 40:
            return self.DB.insertTrainingPicture(pic, user_uuid)
        else:
            return False
