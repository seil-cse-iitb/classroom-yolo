import time
import imutils
import numpy as np
import cv2
import json
import threading
import logging
from hd_variables import variables_hd
from datetime import datetime
from networkLayer import send_HD


class motiondetection(threading.Thread):

	def __init__(self,cycle,data_id,cam_url,threadid):
		threading.Thread.__init__(self)
		self.threadid = threadid
		self.cam_url = cam_url
		self.data_id = data_id
		self.cycle = cycle

	def run(self):
		#print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Starting Motion Detection for Camera " + str(self.threadid+1)
		conf = json.load(open('config_imageprocessing.json'))
		conf_zones = json.load(open('config_zones.json'))

		zone_info = conf_zones[self.data_id]["cameras"]
		for keys in zone_info.keys():
			if str(self.threadid) in keys :
				zone_no = 0
				zone_no=keys

		zone_no = int(zone_no)

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

			if variables_hd.decision[zone_no] == True:
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+ "QUITTING MOTION" + "(Camera " + str(self.threadid) + ")"
				logging.info('Quitting Motion Detection. Another Camera and/or Algorithm gives HD for Zone ' + str(self.zone_no))
				return

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
					camera.release()
					#cv2.destroyAllWindows()
					variables_hd.mutex.acquire()
					logging.info('Mutex Acquired, Camera:' + str(self.threadid +1))
					logging.info('Motion HD, Camera:' + str(self.threadid +1))
					variables_hd.decision[zone_no] = True;
					send_HD(self.data_id,self.cycle,zone_no)
					logging.info('Motion HD, Camera:' + str(self.threadid +1))
					print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+ "Camera " + str(self.threadid) + ":Motion HD"
					variables_hd.mutex.release()
					logging.info('Mutex Released, Camera:' + str(self.threadid +1))
					variables_hd.hd_zone[zone_no] = True

					print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + ": max_contour_size:" +  str(max_contour_area) + ", no_of_contours:" + \
					str(no_of_contours) +  ", HD Timer:" + str(HD_Timer) + ", MOTION:" + str(variables_hd.hd_zone[self.threadid])
					return

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


		variables_hd.hd_zone[self.threadid] = False
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + ": max_contour_size:" +  str(max_contour_area) + ", no_of_contours:" + str(no_of_contours) + \
		", HD Timer:" + str(HD_Timer) + ", MOTION:" + str(variables_hd.hd_zone[self.threadid])
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
