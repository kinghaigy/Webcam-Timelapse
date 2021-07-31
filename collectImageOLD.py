import urllib.request
import time
import datetime
import os


cameraURLPre = "http://192.168.0."
cameraIPs = [30]
cameraNames = ["InsideShearingShed"]
savePath = os.path.normpath("C:/Users/kingh/Desktop/Temporary/camtest/")
logFileName = "runlog.txt"
workStart = 7 # hours
workFinish = 21 # hours



def main():
	# Set our working directory
	os.chdir(savePath)

	# Open log file for writing
	logFile = open(logFileName, "a")

	# Date format string
	timeFileName = time.strftime("%Y-%m-%d-%H-%M-%S")


	# For each camera, Check ok access time build a time stamp filename and save path, save the image
	now = datetime.datetime.now()
	if now.hour >= workStart & now.hour <= workFinish:

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

				urllib.request.urlretrieve(cameraURLPre + str(cam) + "/snap.jpeg", snapFileName)
				#urllib.request.urlretrieve("http://www.dynamicflight.com.au/wp-content/uploads/catablog/thumbnails/gliderstencil-3.png", snapFileName)
			except Exception as e:
				logFile.write(timeFileName + ": " + str(e) + "\r\n")
				exit()

			# Log our success
			logFile.write(timeFileName + ": SUCCES! Logged a snapshot into " + folder + "\r\n")

	# Close the log file and wait for the next run
	logFile.close()


if __name__ == "__main__":
	main()
