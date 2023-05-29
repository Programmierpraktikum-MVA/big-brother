"""Big Brother Database Mangement Class

Manages Database Requests
can Import and Export Pictures from Database

@Author: Julian Flieller <@Dr.Hype#0001>
@Date:   2023-05-13
@Project: ODS-Praktikum-Big-Brother
@Filename: new_database_management.py
@Last modified by:   Julian Flieller
@Last modified time: 2023-05-29
"""
import numpy as np
import pickle
import uuid
import datetime as dt
from pytz import timezone
import pymongo

class BBDB:
    """Database Baseclass""" 
    def __init__(self):
        """
        Builds up the initial connection to the database
        """
        self.cluster = pymongo.MongoClient("mongodb+srv://admin:7EgqBof7tSUKlYBN@bigbrother.qse5xtp.mongodb.net/?retryWrites=true&w=majority",connectTimeoutMS=30000,socketTimeoutMS=None,connect=False,maxPoolsize=1)
        db = self.cluster["BigBrother"]
        self.user= db["user"]
        self.login_attempt = db["login_attempt"]
        self.resource = db["resource"]
        self.resource_context = db["resource_context"]

    def close(self):
        """
        Close the connection with the database
        """
        self.cluster.close()
    
    def closeGraceful(self):
        """
        Should be called everytime the Program Shuts down
        """
        # TODO: Take a look at the use-case of this function. How should it
        # differ from the close-function -> I think it doesnt for mongodb
        self.close()

    def commit(self):
        """
        not needed for mongodb
        """
        # TODO: Talk about it. This might be used somewhere in order
        # to "take back" some entries. -> wdym?
        return

    def delUser(self,user_id)-> bool:
        """
        Delete a user from the database with the given user_id
        """
        if self.user.find_one({"user_enc_res_id":user_id}):
            self.user.delete_one({"user_enc_res_id":user_id})
            return True 
        print("WARNING: Database Login Failed!")
        return False

    def addAdminRelation(self, user_id): 
        """
        Add a user as an admin with the given user_id
        """
        if self.user.find_one({"user_enc_res_id":user_id}):
            self.user.update_one({"user_enc_res_id":user_id},{"$set":{"is_admin":True}})
            return True
        print("WARNING: AddAdminRelation Failed!")
        return False

    def get_username(self,uuids:list):
        """
        Fetches usernames from database belonging to the given uuids

        Arguments:  
        user_enc_res_id -- This is a list of user_uuid. Those are the uuids of which you want to get the usernames.

        Return:  
        Returns the a list of usernames that correspond to the user_uuid 
        that have been inputted. The index i of the return list corresponds
        to user_enc_res_id[i] in the input.
        """
        usernames = []
        for user_enc_res_id in uuids:
            usernames.append(self.user.find_one({"user_enc_res_id":user_enc_res_id})["username"])
        return usernames

    def login_user(self, user_id):
        """
        Creates a new entry in the login_table for the user with the given uuid or username.

        Return:  
        Returns (False,False) if the login fails and the timestamp of the
        login if it succeeds.
        """
        localTime = dt.datetime.now(tz=timezone('Europe/Amsterdam'))
        if self.user.find_one({"user_enc_res_id":user_id}):
            self.login_attempt.insert_one({
                "user_id" : user_id,
                "date" : localTime,
                "login_suc": "",#TODO
                "success_resp_type":int(""),#TODO
                "success_res":"",#TODO
                })

            return localTime
        #TODO let me know what to retrun as an error
        print("WARNING: Database Login Failed!")
        return False
        
    def update_login(self, **kwargs):
        """
        Updates the status of the login of one user with the given user_id

        Keyword arguments:
        user_id -- ID of the user of which you want to log in.
        time -- The timestamp of the login you want to update. 
        success_res -- the uui for the res in the resource table
        """
        user_id = time = inserted_pic_uuid = None
        
        for key, value in kwargs.items():
            if key == "user_id":
                user_id = value
            elif key == "time":
                time = value
            elif key == "success_res":
                success_res = value
        
        if not time or not inserted_pic_uuid or not user_id:
            print("WARNING: Database Login Failed!")
            return False,False
        
        self.login_attempt.update_one(
            {
                "user_id" : user_id,
                "date"      : time
            },
            { "$set" : {
                "success_res" : success_res,
                "login_suc":"",#TODO
                "success_resp_type":int(""),#TODO
                }
             })
        return True

    def register_user(self,username:str):
        """
        Creates a new user in the database with the given username.

        Arguments:  
        username -- The username of the new user.

        Return:  
        If the user has been successfully registered then it returns the
        user_id of the user what has been created.

        Exception:  
        Raises an exception if the username already exists.
        """
        new_uuid = str(uuid.uuid1())

        for existing_uuid in self.getUsers():
            while existing_uuid == new_uuid:
                new_uuid = str(uuid.uuid1())

        if self.user.find_one({"username" : username}):
            raise UsernameExists("Username in use!")
        else:
            self.user.insert_one({
                "username" : username, 
                "user_enc_res_id" : new_uuid,
                "is_admin" : False})
            return new_uuid

    def getUsers(self,limit = -1):
        """
        Fetches all Users with their uuids and usernames from the database

        Optional arguments:  
        limit -- This argument sets the amount of users that you want to limit 
        your request to. If it's set to a negative number (which it is by default),
        then the search isn't limited.

        Return:  
        If `limit` is negative then it returns a dictionary of all users and the 
        associated usernames. If the limit is non-negative then it returns a
        list with `limit` amount of entries. The dictionary key are the user_uuid
        and the value is the username.
        """
        users = self.user.find()
        if limit >= 0:
            users = users.limit(limit)

        user_dict = {}
        for user in users:
            user_dict[user["user_enc_res_id"]] = user["username"]
        return user_dict
            
    def getUserWithId(self, user_id): 
        """
        Returns the username corresponding to the user_id.

        Arguments:
        user_id -- The user_enc_res_id.

        Return:  
        Returns the username corresponding to the user_id. If the user with the
        given ID doesn't exist then None gets returned.
        """
        user_entry = self.user.find_one({"user_enc_res_id" : user_id})
        if user_entry is None: 
            return None
        return user_entry["username"]

    def deleteUserWithId(self,user_id):
        """
        Deletes the user with the given user_uuid from the database and all data cooresponding to it.

        Arguments:
        user_id: ID of the user that should be deleted.

        Return:
        Returns True if the user has been successfully deleted. And 
        False otherwise (e.g. user didn't exist in the database).
        """
        if self.user.find_one({"user_enc_res_id" : user_id}):
            self.delUser(user_id)
            self.login_attempt.delete_many({"user_id" : user_id}) #delete corresponding data as requested
            self.resource.delete_many({"user_id" : user_id}) #delete corresponding data as requested
            #TODO not sure what to do with resource_context though
            return True
        else:
            return False

    def getUser(self, username):
        """
        Returns the uuid corresponding to the username.

        Arguments:  
        username -- The username of the user.

        Return:  
        Returns the uuid corresponding to the username. If the username 
        doesn't exist then it returns None.
        """
        user_entry = self.user.find_one({"username" : username})
        if user_entry is None: 
            return None
        return user_entry["user_enc_res_id"]
    
    def insertTrainingPicture(self, pic:np.ndarray, user_uuid:uuid.UUID):
        """
        Inserts a new training picture into the database and returns the 
        uuid of the inserted picture.

        Arguments:  
        pic       -- Picture to be inserted into the database.
        user_uuid -- ID of the user which owns the picture.

        Return:  
        Returns the uuid of the picture that has been inserted into the database.

        Exception:
        TypeError -- Gets risen if the type of the input isn't the expected type.
        """
        # TODO: Only commented out for testing purposes
        #if type(pic) != np.ndarray or type(user_uuid) != uuid.UUID:
        #    raise TypeError
        
        # TODO: Make sure pic_uuid is unique?
        pic_uuid = str(uuid.uuid1())
        self.wire_train_pictures.insert_one({
            "user_uuid" : user_uuid,
            "pic_data" : pickle.dumps(pic),
            "pic_uuid" : pic_uuid})
        return pic_uuid

    def getTrainingPictures(self, where : str):
        """
        Returns training pictures from the database with the given where clause
        """
        # TODO: Discuss. Change the logic of this function, because the 
        # is hard to parse.
        # TODO: This code is likely not to be correct. Change this code!
        pics,uuids = [],[]
        where = where.replace(" ","") #removes all whitespaces to have a cleaner format to work with
        if "where" == "*":
            for pic in self.wire_train_pictures.find():
                pics.append(pickle.loads(pic["pic_data"]))
                uuids.append(pic["pic_uuid"])
        else:
            pass
            #assuming that where is always of the format """WHERE 'name' = 'John Doe' """
            #self.wire_train_pictures.find({"name":where.split("='")[1].split("'")[0]})
            #pics.append(pickle.loads(pic["pic_data"]))
            #uuids.append(pic["pic_uuid"])
        
        return pics,uuids

    def getAllTrainingsImages(self):
        """
        Returns all training images from the database in three lists: 
        pics, uuids, user_uuids
        """
        pics,uuids,user_uuids=[],[],[]
        for pic in self.wire_train_pictures.find():
            pics.append(pickle.loads(pic["pic_data"]))
            uuids.append(pic["pic_uuid"])
            user_uuids.append(pic["user_uuid"])
        return pics, uuids, user_uuids

    def insertPicture(self, pic : np.ndarray, user_uuid : uuid.UUID):
        # TODO: Take a look at what this funciton is supposed to do. 
        # Decide whether you want to implement it or not.

        # Returns True/False on Success or Error
        # Pickles Picture and inserts it into DB
        # pic : picture to be saved as np.ndarray
        # user_uuid : id of user wich owns picture

        # TODO: Error Handling, in the rare case that a duplicate 
        # uuid is generated this method has to try again
        
        raise NotImplementedError

    def getPicture(self,query : str):
        # TODO: was not implemented yet
        raise NotImplementedError

class opencv_DB(BBDB):
    # TODO: Discuss. REMOVEABLE? -> lmk
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class frontend_DB(BBDB):
    # TODO: Discuss. REMOVEABLE? -> lmk
    def __init__(self,dbhost:str=None):
        BBDB.__init__(self)


class UsernameExists(Exception):
    pass

"""
# only for testing, remove in production
if __name__ == '__main__':
    DB = BBDB()
    DB.register_user("mike")
    print(list(DB.user_table.find()))
"""
