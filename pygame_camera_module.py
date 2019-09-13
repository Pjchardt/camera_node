#simple class to grab webcam frames using pygame camera

import os
import pygame
import pygame.camera


class PygameCameraModule(object):
    #def __init__(self):

    def start(self):
        pygame.camera.init()
        cameras = pygame.camera.list_cameras() #Camera detected or not
        print(cameras)
        print ("Using camera %s ..." % cameras[0])
        self.cam = pygame.camera.Camera(cameras[0], (640, 480))
        self.cam.start()

    def capture_image(self, name):
        img = self.cam.get_image()
        img = pygame.transform.rotate(img, -90)
        img = pygame.transform.smoothscale(img, (960, 1280))
        pygame.image.save(img,name)
