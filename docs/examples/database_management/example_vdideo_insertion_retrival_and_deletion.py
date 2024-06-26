###############################################
#         Make THIS script executable         #
###############################################
import sys
import os
import mongomock
from mongomock.gridfs import enable_gridfs_integration
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "database_management"))

# for testing environment
enable_gridfs_integration()

###############################################
#       The actual program starts here        #
###############################################
from video_database import VideoDatabase

# getting DB instance for video management:
# If you want to try it out locally then you can insert your client 
# as parameter into the constructor.
# for local testing use: 
db = VideoDatabase(mongomock.MongoClient())
# db = DBM.vid_DB()

# We assume user_id is the ID of a user from which you want to insert the video
# FOR TEST PURPOSES we register a new user
user_encoding = None
user_id = db.register_user("new_user", None)

# insert video stream
video_source = "../../../res/videos/prog_in_c.mp4"
filename = "someFilename"
video_transcript = "someTranscript"
stream_insert = open(video_source, "rb+")
vid_id = db.insert_video(stream_insert, user_id, filename, video_transcript)
stream_insert.close()

# Get video ids of a certain user
vid_ids_of_user = db.get_video_id_of_user(user_id)

# get stream
video_destination = "tmp.mp4"
stream_get = open(video_destination, "wb+")
vid_id_, filename_, video_transcript_ = db.get_video_stream(vid_id, stream_get)
stream_get.close()

# delete video
db.delete_video(vid_id)
