from datetime import datetime, timedelta
import logging
import os
import time
import datetime
import sys
import glob
import re
import subprocess
import copy
from camera import Camera

########################################
######### CAMERA CONFIGURATION #########
########################################

# If this is running on the same machine that collects the images, you can use
# the same camera details with the below import

# from webcamTimelapse import cameraList

# Otherwise, specify the cameras you wish with empty string URLS with the correct path to images
cameraList = []
cameraList.append(Camera("Harrison & Tamsin's House", "", os.path.normpath("//192.168.10.2/File Shares/Timelapse/HazzTamsinHouse"), 6, 19, 5))



class TimelapseImage():
    def __init__(self, imageURI):
        logging.getLogger()
        self.imageURI = imageURI

        # get the actual filename from the path.
        self.fileName = os.path.basename(imageURI)
        dateString = self.fileName.split(".")
        dateString = dateString[0] 
        
        # Try to convert filename to actual datetime object.
        self.dateAndTime = datetime.datetime.strptime(dateString, "%Y-%m-%d-%H-%M-%S")


def buildRawImageArray(pathToImageFolder):
    # Globs all images in the path paramater and builds an array of TimelapseImages to return for further filtering.
    fileList = 0
    imageArray = []
    try:
        fileList = glob.glob(pathToImageFolder + "\*.jpg")
    except:
        logging.error("Somehow struggled to glob files for " + pathToImageFolder)
    
    for file in fileList:
        imageArray.append(TimelapseImage(file))
    
    return imageArray

def filterImageArrayByDateTime(imageArray, dateAndTime, timeDelta):
    # We loop through the image array and populate a filtered arrray that matches images
    # between dateAndTime and dateAndTime + timeDelta
    #
    # Filtering between 7AM and 7PM would have a time delta of 12H.

    filteredArray = []
    for image in imageArray:
        if image.dateAndTime >= dateAndTime and image.dateAndTime <= (dateAndTime + timeDelta):
            filteredArray.append(image)

    return filteredArray

def buildFFMPEGFile(imageArray, fileName):
    # Check if the folder exists, if not then make it
    if not os.path.isdir(savePath):
        os.makedirs(savePath)
    
    # Is the image array empty? Working through a date range with empty dates will produce an empty array
    # in this case, we want to do nothing.
    if (len(imageArray) == 0):
        return ""


    # image array contains a bunch of image objects. Populate a list ready for ffmpeg.
    if os.path.isfile(fileName):
        logging.info(fileName + " already exists. It has been replaced.")
    ffmpegList = open(fileName, 'w')

    for image in imageArray:
        ffmpegList.write("file '" + image.imageURI +  "'\r\n")

    logging.info("FFMPEG image list created: " + fileName)
    
    return fileName

def buildVideoFile(ffmpegInput, outputVideoFile):
    # Doesn't check if file exists. Just overwrites it. 
    subprocess.run(["ffmpeg","-y", "-r", "30", "-f", "concat", "-safe", "0", "-i", ffmpegInput, "-vcodec", "libx264", "-crf", "18", "-pix_fmt", "yuv420p" , outputVideoFile])


def buildVideos():
    for camera in cameraList:
        # Loop through all cameras we have listed and create timelapses for them
        videoPath = os.path.join(camera.savePath, "videos")
        if not os.path.isdir(videoPath):
            os.makedirs(videoPath)
        images = buildRawImageArray(camera.savePath)

        # find the earliest dated image.
        minDate = datetime.datetime(2100,1,1)
        for image in images:
            if image.dateAndTime < minDate:
                minDate = image.dateAndTime

        # Set start datetime and time deltas
        startDate = datetime.datetime(minDate.year, minDate.month, minDate.day, minDate.hour, minDate.minute, minDate.second)
        workTimeDelta = datetime.timedelta(hours = camera.stopTime - camera.startTime)

        # build all time lapse file lists until right now
        endDateTime = datetime.datetime.now()

        while startDate <= endDateTime:
            filtered = filterImageArrayByDateTime(images, startDate,workTimeDelta)
            fileName = os.path.join(videoPath, startDate.strftime("%Y-%m-%d") + ".txt")
            buildFFMPEGFile(filtered, fileName)
            startDate = startDate + datetime.timedelta(days=1)

        # Lets try to build all lists in a folder
        ffmpegLists = glob.glob(videoPath + "/*.txt" )
        for imageList in ffmpegLists:

            # Check does our video file exist already? If so, skip it.
            videoFileName = os.path.join(videoPath,  imageList.split('.txt')[0] + ".mp4")
            if os.path.isfile(videoFileName):
                logging.info("Didn't create a video for input file " + imageList + " as a video for it already exists. Delete that file and run this again if you want it remade.")
                pass
            else:
                buildVideoFile(imageList, videoFileName)
    


if __name__ == "__main__":
    savePath = os.path.normpath(os.getcwd())
    logging.basicConfig(filename= savePath + "/TimeLapseBuilder.log", encoding='utf-8', level=logging.DEBUG, format="%(asctime)s: [%(levelname)s] - %(message)s")
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

    buildVideos()
    exit()
        



        



