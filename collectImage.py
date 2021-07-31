import urllib.request
import time
import datetime
import sys
import os
import glob
import re
import subprocess
import copy


cameraURLPre = "http://192.168.0."
cameraIPs = [44]
camerasGlobbed = []
cameraGlobs = []
cameraNames =  ["OutsideShearingShed"]
savePath = os.path.normpath("E:/TEMP/ProcessingPlantTimelapse/")
logFileName = "runlog.txt"
workStart = 7 # hours
workFinish = 19 # hours
ffmpegSettings = ["-r", "30", "-f", "concat", "-safe", "0", "-vcodec", "libx264", "-crf", "25", "-pix_fmt", "yuv420p"]




def main():

	# Date format string
	timeFileName = time.strftime("%Y-%m-%d-%H-%M-%S")


	# For each camera, Check ok access time build a time stamp filename and save path, save the image
	now = datetime.datetime.now()
	if now.hour >= workStart and now.hour < workFinish:

		# Inside working hours
		for cam in range(0, len(cameraIPs)):

			# Try to access the folder name array
			try:
				folder = cameraNames[cam]

			except Exception as e:
				logFile.write(timeFileName + ": Error reading camera name. Is there 1:1 camera IPs and names?\r\n")
				exit()

			# Check if the folder exists, if not then make it
			if not os.path.isdir(folder):
				os.makedirs(folder)
					
			# Build the file name 
			snapFileName = folder + "/" + timeFileName + ".jpeg"

			# Try to get the picture from the camera
			try:
				print("Attempting to retrieve " + cameraURLPre + str(cameraIPs[cam]) + "/snap.jpeg")

				urllib.request.urlretrieve(cameraURLPre + str(cameraIPs[cam]) + "/snap.jpeg", snapFileName)
			except Exception as e:
				logFile.write(timeFileName + ": " + str(e) + "\r\n")
				exit()

			# Log our success
			logFile.write(timeFileName + ": SUCCES! Logged a snapshot into " + folder + "\r\n")

	exit()

def getListOfFiles(camera):
	# Gets a list of files for that camera. Returns a list of all pictures in CameraName/imageName.jpeg format

	# If the camera has been globbed once before, use the previous results. 
	if camera not in camerasGlobbed:
		# Glob this camera and make reference to the results
		cameraGlobs.append(glob.glob(camera + "\*.jpeg"))

		# Add this camera to the list of globbed cameras. 
		camerasGlobbed.append(camera)
		
	return  cameraGlobs[camerasGlobbed.index(camera)]
	

def filterCorruptFiles(listOfFiles):
	for line in listOfFiles[:]:
		if os.path.getsize(line) < 127000:
			listOfFiles.remove(line)
	return listOfFiles

def filterPhotosByDate (dateObj, listOfFiles):
	datePattern = dateObj.strftime("%Y-%m-%d")
	regex = re.compile(datePattern + r'.*')
	return list(filter(regex.search, listOfFiles))

def buildDailyLists(currentDate, cameraName): 
	# This function builds the list of all the images taken on currentDate by cameraName ready to make a video
	# It will ignore files that are under 100 kbytes as they are generally corrupted anyway.

	pictureList = getListOfFiles(cameraName) # Slow - repeated way too often. CBF changing as this will be run once.
	pictureList = filterCorruptFiles(pictureList)
	pictureList = filterPhotosByDate(currentDate, pictureList)

	# Picture list now contains a list of today's photos written as CameraName\XX-XX-XX-XX-XX-XX.jpeg
	dailyFileList = open(cameraName + "DailyList.txt", 'w')
	for line in pictureList:
		dailyFileList.write("file '" + savePath + "\\" + line + "'\r\n")

	logFile.write("Made a daily list for " + cameraName + "\r\n")



def buildCompleteLists():
	# This function builds the list of all the images taken ever ready to make a video
	# It will ignore files that are under 127 kbytes as they are generally corrupted anyway.

	for camera in cameraNames:
		pictureList = getListOfFiles(camera)
		pictureList = filterCorruptFiles(pictureList)

		# Picture list now contains a list of today's photos written as CameraName\XX-XX-XX-XX-XX-XX.jpeg
		completeFileList = open(camera + "CompleteList.txt", 'w')
		for line in pictureList:
			completeFileList.write("file '" + savePath + "\\" + line + "'\r\n")

		logFile.write("Made a complete list for " + camera + "\r\n")


def buildDailyVideos(currentDate, cameraName): 
	# Build a clip of the action specified in cameraNameDailyList.txt (produced after running buildDailyLists)

	# Make a file name:
	timeFileName = currentDate.strftime("%Y-%m-%d") + ".mp4"

	# Make the clips subfolder if it doesn't already exist.
	if not os.path.exists(cameraName + "\\Clips"):
		os.makedirs(cameraName + "\\Clips")
	subprocess.run(["ffmpeg", "-r", "30", "-f", "concat", "-safe", "0", "-i", savePath + "\\" + cameraName + "DailyList.txt", "-vcodec", "libx264", "-crf", "25", "-pix_fmt", "yuv420p" , savePath + "\\" + cameraName + "\\Clips\\" + timeFileName])

def combineDailyVideos():

	for camera in cameraNames:

		# Today's video name:
		timeFileName = time.strftime("%Y-%m-%d") + ".mp4"

		# Today's File Path:
		filePath = savePath + "\\" + camera + "\\Clips\\"

		# Check if there is an existing combined video
		if not os.path.exists(camera + "\\Clips\\Combined.mp4"):
			print("path doesnt' exist")
			# If not, copy the single video to the place the combined one will be. 
			os.system("copy " + filePath + timeFileName + " " + filePath + "Combined.mp4")
		else:
			# There is a video there, combine it.


			# We need to make a temporary file to list the files to concat. I can't find a way around this.
			tempFile = open("temp.txt", 'w')
			tempFile.write("file '" + filePath + "Combined.mp4'\r\n")
			tempFile.write("file '" + filePath + timeFileName + "\r\n")
			tempFile.close()


			print("path does exist")
			subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "temp.txt", "-c", "copy", filePath + "Combined.mp4"])
			#ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4s



if __name__ == "__main__":
	# Set our working directory
	os.chdir(savePath)

	# Open log file for writing
	logFile = open(logFileName, "a")


	if "-buildDailyLists" in sys.argv:
		buildDailyLists()
		exit()

	if "-buildCompleteList" in sys.argv:
		buildCompleteLists()
		exit()

	if "-buildDailyVideos" in sys.argv:
		buildDailyVideos()
		exit()

	if "-combineDailyVideos" in sys.argv:
		combineDailyVideos()
		exit()

	if "-buildAllDailyVideos" in sys.argv:
		startDate = datetime.date(2017,11,29)
		endDate = datetime.date(2018,6,14)
		dayIncrement = datetime.timedelta(days=1)

		for camera in range(0, len(cameraIPs)):
			currentDate = copy.deepcopy(startDate) #TRYING TO COPY CONSTRUCT
			
			while currentDate <= endDate:
				#build a list of the pics to put in this date's video 
				buildDailyLists(currentDate, cameraNames[camera])

				# We should have a txt document with a list of pictures to use. Lets compile it into a video
				buildDailyVideos(currentDate, cameraNames[camera])

				# At the end, we have a new clip. Increment our date 
				currentDate = currentDate + dayIncrement



	if "-test" in sys.argv:
		listOfFiles = getListOfFiles(cameraNames[1])
		#print(listOfFiles)

		print("That was a list of pictures, here's the size of the list with corrupts remove")
		print(len(listOfFiles))
		cleanListOfFiles = filterCorruptFiles(listOfFiles)
		print(len(cleanListOfFiles))
		now = datetime.datetime.now()
		dateListOfFiles = filterPhotosByDate(now, cleanListOfFiles)
		print(len(dateListOfFiles))

		exit()

	# If nothing has been specified, capture images as normal
	main()

	# Close the log file
	logFile.close()
