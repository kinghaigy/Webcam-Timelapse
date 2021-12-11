from datetime import datetime
import time
import os
import logging
import urllib.request
import glob
import re
from exif import Image


class Camera():
    def __init__(self, name, URL, savePath, startTime, stopTime, interval):
        logging.getLogger()
        # check types
        if not isinstance(name, str):
            raise Exception("name parameter must be a string")
        
        if not isinstance(URL, str):
            raise Exception("URL parameter must be a string")

        if not isinstance(savePath, str):
            raise Exception("savePath parameter must be a string")
        
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
        self.savePath = os.path.normpath(savePath)
        self.glob = None

        # can we save to the save path right now?
        if not os.path.isdir(self.savePath):
            logging.info(self.savePath + " didn't exist. Making it now")
            os.makedirs(self.savePath)

    
    def startTimelapse(self):
        self.running = True
        while self.running:
            # Moved the sleep to the top to work with the 'continue' statement when an image doesn't get saved.
            time.sleep(self.interval)

            # Are we inside working hours?
            now = datetime.now()
            if now.hour >= self.startTime and now.hour < self.stopTime:
                print("Saving image from: " + self.name)
                snap = None
                try:
                    snap = urllib.request.urlopen(self.URL)

                    # is the image corrupted? (smaller than 90kb)
                    if (snap.length < 90000):
                        logging.error("Image appears to be corrupt: " + self.URL)
                        continue
                except Exception as e:
                    logging.error("Couldn't retrieve image at URL: " + self.URL)
                    continue

                
                # We at least retrieved something from the URL. Going to assume it was an image.

                image = Image(snap)
                timeFileName = time.strftime("%Y-%m-%d-%H-%M-%S") + ".jpg" # Going to filter by name for future image making so best to have a nice name.
                try:
                    with open(self.savePath + "/" + timeFileName, 'wb') as new_image_file: # make this less flakey for proper release
                        new_image_file.write(image.get_file())
                except Exception as e:
                    logging.error("Couldn't write image to disk at " + timeFileName)


    
    def stopTimelapse(self):
        self.running = False
    
    def getImageList(self):
        # This returns a list of escaped paths. If you're running on windows, you'll see D:\\Harrison\\ etc, 
        if self.glob == None:
            # not globbed yet.
            self.glob = glob.glob(self.savePath + "/*.jpg")
        return self.glob

    # FUNCTION HUGELY IMPCOMPLETE. CBF FINISHING RIGHT NOW
    def getFilteredImageList(self, dateTimeStart, duration=1):
        class DatedImage():
            def __init__(self, path):
                self.path = path
                self.dateTime = None

        imageList = self.getImageList()
        datedImageList = []

        for image in imageList:
            dateImage = DatedImage(image)
            datedImageList.append(DatedImage())
        # Need to make a list of 
        datePattern = dateTimeStart.strftime("%Y-%m-%d")
        regex = re.compile(datePattern + r'.*')
        return list(filter(regex.search, imageList))

