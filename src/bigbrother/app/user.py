"""
TODO: Add a description of the module
"""

import io
import uuid
import base64

import numpy as np
from flask_login import UserMixin
from PIL import Image


class BigBrotherUser(UserMixin):
    """
    This class keeps the information about the user.
    """

    # TODO: The user shouldn't store data about the database.
    # -> Discuss whether it really should be done.
    # TODO: Verify whether the uuids are really all from type uuid.UUID.
    def __init__(self, user_uuid: uuid.UUID, name: str, DB):
        self.uuid = user_uuid
        self.name = name
        self.DB = DB

        # TODO: We should not allow it to be a tuple!
        if type(user_uuid) == tuple:
            self.uuid = user_uuid[0]

        self.trainingPictures = []
        """ logData: Used for logs. Stores past login dates as well as
        the picture IDs that are associated with those logins that came
        from the user with the uuid: self.uuid"""
        self.logData = []
        self.trainingPicturesWebsiteFormat = []

        self.admin = False
        self.childUser = []

        self.sync()

        self.recogFlag = False

    def sync(self):
        pics, uuids = self.DB.getTrainingPictures(user_uuid=self.uuid)
        self.trainingPicturesWebsiteFormat = []

        for pic_index, pic in enumerate(pics):
            try:
                if (pic.shape[0] == 0) or (pic.shape[1]) == 0:
                    pic = np.random.randint(255, size=(10, 10, 3), dtype=np.uint8)

                file_object = io.BytesIO()
                img = Image.fromarray(pic.astype('uint8'))
                img.save(file_object, 'PNG')
                base64img = "data:image/png;base64," + base64.b64encode(file_object.getvalue()).decode('ascii')
                self.trainingPicturesWebsiteFormat.append((uuids[pic_index], base64img))
                self.trainingPictures.append((uuids[pic_index], pic))
            except ValueError:
                print("ValueError: Illegal Image Loaded!")
                print("User: {}\n UUID: {}\npic_uuid: {}".format(self.name, self.uuid, uuids[pic_index]))
                return

        self.logData = self.DB.getLoginLogOfUser(user_uuid=self.uuid)
        # TODO: Setting permissions for admin?
        """
        admin_collection = self.DB['admin_table']
        query = {"admin_uuid": str(self.uuid)}
        result = admin_collection.find(query)

        self.childUser = []
        for document in result:
            child_user = document['child_user']
            self.admin = True
            self.childUser.append(child_user)
        """
        # TODO: What is this supposed to do? Is it ther to build some sort of
        # hierarchy?
        self.childUser = []

    def get_id(self):
        return self.uuid
