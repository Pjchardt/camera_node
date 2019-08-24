import json
import pyrebase
import re

try:
    from urllib.parse import urlencode, quote
except:
    from urllib import urlencode, quote

from pymitter import EventEmitter

class PyrebaseDatabase(object):
    def __init__(self):
        with open('pyrebase_config.json') as f:
            self.config = json.load(f)
        with open('database_paths_config.json') as f:
            self.paths_config = json.load(f)

        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()
        self.storage = self.firebase.storage()
        self.token = self.auth.create_custom_token("pjchardt")

        self.auth_user()
        #TODO: we need to start timer and refresh user token before an hour is up

        self.node_path = "{0}/{1}".format(self.paths_config['node_root'], self.paths_config['node'])
        #get current index and max index
        self.current_index = self.db.child(self.node_path).child(self.paths_config['index']).get().val()
        self.max_index = self.db.child(self.node_path).child(self.paths_config['max_index']).get().val()

    def auth_user(self):
            try:
                self.user = self.auth.sign_in_with_custom_token(self.token)
            except requests.exceptions.ConnectionError as conn_err:
                print("failed to auth user, trying again")
                self.auth_user()

    def start(self):
        self.ee = EventEmitter()
        self.new_data_listener(self.new_data_handler)
        self.my_stream = self.db.child("some child node").stream(self.stream_handler)

    def stop(self):
        print('shutting down firebase')
        self.my_stream.close()

    def stream_handler(self, message):
            print(message["event"]) # put
            print(message["path"]) # /-K7yGTTEp7O549EzTYtI
            print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}
            s = json.dumps(message["data"])
            self.ee.emit("new_data_event", s)

    def new_data_handler(self, args):
        print(args)

    def new_data_listener(self, func):
        self.ee.on("new_data_event", func)

    def send_data(self, node, data):
        self.db.child(node).update(data);

    def send_image(self, image_path):
        storage_path = "{0}{1}.jpg".format(self.paths_config['storage_path'], self.current_index)
        # upload image to storage
        result = self.storage.child(storage_path).put(image_path, self.user['idToken'])
        #get url for downloading image
        firebase_url = "https://firebasestorage.googleapis.com/v0/b/"
        storage_bucket = self.config["storageBucket"]
        token = result['downloadTokens']
        url = "{0}{1}/o/{2}?alt=media&token={3}".format(firebase_url, storage_bucket, quote(storage_path, safe=''), token)
        print ("Image sent. url = " + url)
        #update database with url
        self.db.child(self.node_path).update({"url_{0}".format(self.current_index) : url});
        self.current_index = (self.current_index + 1) % self.max_index
        self.db.child(self.node_path).update({self.paths_config['index'] : self.current_index })
