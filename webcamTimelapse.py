import urllib.request
import time
from datetime import datetime
import os
from camera import Camera
import logging
from multiprocessing import Process
import urllib.request
from exif import Image
import sys

###############################################
#                   CONFIG                    #
###############################################

savePath = os.path.normpath(os.getcwd() + "/images/")
logging.basicConfig(filename= savePath + "timelapse.log", encoding='utf-8', level=logging.DEBUG, format="%(asctime)s: [%(levelname)s] - %(message)s")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
ffmpegSettings = ["-r", "30", "-f", "concat", "-safe", "0", "-vcodec", "libx264", "-crf", "25", "-pix_fmt", "yuv420p"]

# Add cameras here
cameraList = []
cameraList.append(Camera("New Shed", "http://192.168.0.31/snap.jpeg", savePath + "/NewShed", 0, 24, 5))
cameraList.append(Camera("Harrison & Tamsin's House", "http://192.168.0.27/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=as1234&user=admin&password=harrison", savePath + "/HazzTamsinHouse", 0, 24, 5))




###############################################
#                  BUSINESS                   #
###############################################
def main():
    logging.info("Staring up the time lapse system for " + str(len(cameraList)) + " cameras:")
    proc = []

    for camera in cameraList:
        logging.info("   " + camera.name)
        p = Process(target = camera.startTimelapse, daemon = True)
        proc.append(p)
        p.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for p in proc:
            p.join()


if __name__ == '__main__':
    main()

