import time
import imutils
import numpy as np
import cv2
import json
import threading
from hd_variables import variables_hd
from facedetection import face_detection
from datetime import datetime

class run_yolo(threading.Thread):

	def __init__(self,cam_url,threadid):
		threading.Thread.__init__(self)
		self.threadid = threadid
		self.cam_url = cam_url


	def run(self):
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Starting Motion Detection for Camera " + str(self.threadid+1)
		HD=False
		conf = json.load(open('config_imageprocessing.json'))
		HD_Timer =0
		ThresholdArea = conf["Threshold Area"]

		if self.threadid == 2:
			ThresholdArea = 0

		connection = False
		camera = cv2.VideoCapture(self.cam_url)
		start = time.time()
		firstFrame = None

		max_contour_area = 0
		no_of_contours = 0

		while(not connection):
			try:
				_, frame = camera.read()
				connection = True

			except:
				camera = cv2.VideoCapture(self.cam_url)
				print camera

		# loop over the frames of the video
		while True:

			(grabbed, frame) = camera.read()

			if grabbed is None:
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Waiting"
				continue

			#original_feed = frame
			try:
				frame = imutils.resize(frame, conf["frame width"])
				gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
				gray = cv2.GaussianBlur(gray, (21, 21), 0)

			except:
				print "opencv error: frame not found. Please check camera " + str(self.cam_url)
				return

			if firstFrame is None:
				firstFrame = gray
				continue

			frameDelta = cv2.absdiff(firstFrame, gray)
			firstFrame = gray

			thresh = cv2.adaptiveThreshold(frameDelta,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)
			thresh = cv2.dilate(thresh, None, iterations=3)
			cnts, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)[-2:]
			contourcheck = len(cnts)
			no_of_contours += len(cnts)

			for i in range(len(cnts)):
				if(cv2.contourArea(cnts[i]) < ThresholdArea):
					contourcheck = contourcheck - 1
					no_of_contours -= 1
					continue

				#print cv2.contourArea(cnts[i])

				if cv2.contourArea(cnts[i])>max_contour_area:
					max_contour_area = cv2.contourArea(cnts[i])

				(x, y, w, h) = cv2.boundingRect(cnts[i])

				cv2.drawContours(frame, cnts, i,(244,233,0))
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

			if (contourcheck>0):
				HD_Timer += 1
				if HD_Timer  > 25:
					#print HD_Timer
					HD = True
					camera.release()
					#cv2.destroyAllWindows()
					print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + ": max_contour_size:" +  str(max_contour_area) + ", no_of_contours:" + str(no_of_contours) +  ", HD Timer:" + str(HD_Timer) + ", MOTION:" + str(HD)
					variables_hd.cam_url_hd[self.threadid] = HD
					return

			#else:
				#HD_Timer = 0

			if HD_Timer>25:
				HD = True
				#filename = "/home/stark/BA/Malvika/Presence/" + str(time.strftime("%H %M %S")) + "_" +  str(int(max_contour_area)) + ".jpg"
				#print filename
				#cv2.imwrite(filename,frame)

			if conf["show_video"]:
				cv2.imshow("Motion Detection", frame)

			#key = cv2.waitKey(1) & 0xFF
			if ((time.time() - start) > conf["T_Check"]):
				break

		camera.release()
		#cv2.destroyAllWindows()
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + ": max_contour_size:" +  str(max_contour_area) + ", no_of_contours:" + str(no_of_contours) +  ", HD Timer:" + str(HD_Timer) + ", MOTION:" + str(HD)

		variables_hd.cam_url_hd[self.threadid] = HD
		return


def skin_detection(image, x,y,w,h):
	# Constants for finding range of skin color in YCrCb
	min_YCrCb = np.array([0,133,77],np.uint8)
	max_YCrCb = np.array([255,173,127],np.uint8)

	# Convert image to YCrCb
	imageYCrCb = cv2.cvtColor(image,cv2.COLOR_BGR2YCR_CB)

	# Find region with skin tone in YCrCb image
	skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)

	area = w*h
	count=0.0

	for i in range(y,y+h):
		for j in range(x,x+w):
			if skinRegion[i][j]==255:
				count+=1.0

	percentage=(count/area)*100

	if percentage > 0:
		return True

	else:
		return False
