import os
import json
import pyrebase
import re
import requests
#from threading import Timer

try:
    from urllib.parse import urlencode, quote
except:
    from urllib import urlencode, quote

from pymitter import EventEmitter

class PyrebaseDatabase(object):
    def __init__(self):
        dirname, filename = os.path.split(os.path.abspath(__file__))
        print(dirname)
        with open("{0}{1}".format(dirname, "/pyrebase_config.json")) as f:
            self.config = json.load(f)
        with open("{0}{1}".format(dirname, "/database_paths_config.json")) as f:
            self.paths_config = json.load(f)
        
        self.config['serviceAccount'] = "{0}/{1}".format(dirname, self.config['serviceAccount'])
        print(self.config['serviceAccount'])
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        self.storage = self.firebase.storage()
        self.token = self.auth.create_custom_token("pjchardt")

        self.auth_user()
        #Start timer to reauth
        #self.t = Timer(60.0, self.reauth_user)
        #self.t.start()

        self.node_path = "{0}/{1}".format(self.paths_config['node_root'], self.paths_config['node'])

    def auth_user(self):
        try:
            self.user = self.auth.sign_in_with_custom_token(self.token)
        except requests.exceptions.ConnectionError as conn_err:
            print("failed to auth user, trying again")
            self.auth_user()

    def reauth_user(self, image_path):
        self.user = self.auth.refresh(self.user['refreshToken'])
        self.send_image(image_path)

    def start(self):
        self.ee = EventEmitter()
        self.new_data_listener(self.new_data_handler)
        self.my_stream = self.db.child("some child node").stream(self.stream_handler)

    def stop(self):
        print('shutting down firebase')
        #self.my_stream.close()
        #self.t.abort()

    def stream_handler(self, message):
        print(message["event"]) # put
        print(message["path"]) # /-K7yGTTEp7O549EzTYtI
        print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
        s = json.dumps(message["data"])
        self.ee.emit("new_data_event", s)

    def get_indexes(self):
        #get current index and max index
        i = self.db.child(self.node_path).child(self.paths_config['index']).get().val()
        max_i = self.db.child(self.node_path).child(self.paths_config['max_index']).get().val()
        return i, max_i 

    def new_data_handler(self, args):
        print(args)

    def new_data_listener(self, func):
        self.ee.on("new_data_event", func)

    def send_data(self, node, data):
        self.db.child(node).update(data);

    def send_image(self, image_path):
        current_index, max_index = self.get_indexes()
        storage_path = "{0}{1}.jpg".format(self.paths_config['storage_path'], current_index)
        # upload image to storage
        #instead of reauth on timer we should catch error inside this function and then call reauth
        try:
            result = self.storage.child(storage_path).put(image_path, self.user['idToken'])
        except requests.exceptions.HTTPError:
            #reauth user, then call this method again
            print("storage put failed with HTTPError, calling reauth_user to try and resolve")
            reauth_user(image_path)

        #get url for downloading image
        firebase_url = "https://firebasestorage.googleapis.com/v0/b/"
        storage_bucket = self.config["storageBucket"]
        token = result['downloadTokens']
        url = "{0}{1}/o/{2}?alt=media&token={3}".format(firebase_url, storage_bucket, quote(storage_path, safe=''), token)
        print ("Image sent. url = " + url)
        #update database with url
        self.db.child(self.node_path).update({"url_{0}".format(current_index) : url});
        current_index = (current_index + 1) % max_index
        self.db.child(self.node_path).update({self.paths_config['index'] : current_index })
