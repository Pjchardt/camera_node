import subprocess
import platform
import time

import database as DB
import input_commands as IC
import pygame_camera_module as CM

class Main(object):
    def __init__(self):
        #Setup input events
        IC.InputCommands(self.shutdown)
        #Connect to firebase
        self.db = DB.PyrebaseDatabase()
        self.cam = CM.PygameCameraModule()
        self.cam.start()

    def start(self):
        self.run()

    def run(self):
        self.run_loop = True
        #Loop until 'esc' pressed
        while self.run_loop:
            #capture image
            self.cam.capture_image("capture.jpg")
            #send image, get url, and save to database
            self.db.send_image("capture.jpg")
            time.sleep(60*5)

    def shutdown(self):
        print('stopping application')
        self.run_loop = False

m = Main()
m.start()
