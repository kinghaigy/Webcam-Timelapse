import time
from threading import *

class Camera(Thread):
    def __init__(self, name, URL, startTime, stopTime, interval):
        
        # Threading
        Thread.__init__(self, target=self.startTimelapse)
        self.daemon = True

        # check types
        if not isinstance(name, str):
            raise Exception("name parameter must be a string")
        
        if not isinstance(URL, str):
            raise Exception("URL parameter must be a string")
        
        if not isinstance(interval, int):
            raise Exception("interval must be an integer > 0")

        if not isinstance(startTime, int):
            raise Exception("startTime parameter must be an integer between 0-24")

        if not isinstance(stopTime, int):
            raise Exception("stopTime parameter must be an integer between 0-24")
        
        if (startTime > 24 or startTime < 0):
            raise Exception("startTime parameter must be an integer between 0-24")
        
        if (stopTime > 24 or stopTime < 0):
            raise Exception("stopTime parameter must be an integer between 0-24")

        if (interval <= 0):
            raise Exception("interval must be an integer > 0")

        self.name = name
        self.URL = URL
        self.startTime = startTime
        self.stopTime = stopTime
        self.interval = interval
    
    def startTimelapse(self):
        self.running = True
        while self.running:
            print("saving image from: " + self.name)
            time.sleep(self.interval)
    
    def stopTimelapse(self):
        self.running = False
        self.join()
    

        


