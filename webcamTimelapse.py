import urllib.request
import time
import datetime
import sys
import os
import glob
import re
import subprocess
import copy
from camera import Camera
import logging
import asyncio
from multiprocessing import Process



###############################################
#                   CONFIG                    #
###############################################

#savePath = os.path.normpath("~/timeLapse/")
savePath = ""
ffmpegSettings = ["-r", "30", "-f", "concat", "-safe", "0", "-vcodec", "libx264", "-crf", "25", "-pix_fmt", "yuv420p"]
logging.basicConfig(filename= savePath + "timelapse.log", encoding='utf-8', level=logging.DEBUG)

# Add cameras here
cameraList = []
cameraList.append(Camera("New Shed1", "192.168.0.31/snap.jpeg", 6, 8, 5))
cameraList.append(Camera("New Shed2", "192.168.0.31/snap.jpeg", 6, 8, 5))
cameraList.append(Camera("New Shed3", "192.168.0.31/snap.jpeg", 6, 8, 5))





###############################################
#                  BUSINESS                   #
###############################################
print("Staring up the time lapse system for " + str(len(cameraList)) + " cameras:")
logging.info("Staring up the time lapse system for " + str(len(cameraList)) + " cameras:")
proc = []

for camera in cameraList:
    print("  - " + camera.name)
    logging.info("  - " + camera.name)
    camera.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    for camera in cameraList:
        camera.stopTimelapse()