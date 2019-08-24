from pynput import keyboard
from threading import Thread

from pymitter import EventEmitter

class InputCommands(object):
    def __init__(self, func):
        #Setup listeners for input
        thread = Thread(target = self.key_listener)
        thread.start()
        self.ee = EventEmitter()
        self.ee.on("exit_event", func)

    #Input callbacks
    def on_release(self, key):
        print('{0} released'.format(key))
        if key == keyboard.Key.esc:
            self.ee.emit("exit_event")
        return False

    def key_listener(self):
        # Collect events until released
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()