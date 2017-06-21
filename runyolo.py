import time
import numpy as np
import cv2
import json
import threading
from hd_variables import variables_hd
from datetime import datetime
from networkLayer import send_HD
import subprocess
import os
import logging

class run_yolo(threading.Thread):

	def __init__(self,cycle,data_id,cam_url,threadid):
		threading.Thread.__init__(self)
		logging.info("Yolo Initialization started")
		self.threadid = threadid
		self.cam_url = cam_url
		self.data_id = data_id
		self.cycle = cycle
		logging.info("Yolo Initialization Ended")

	def run(self):
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Starting YOLO for Camera " + str(self.threadid+1)
		HD=False
		conf = json.load(open('config_imageprocessing.json'))

		conf_zones = json.load(open('config_zones.json'))

		zone_info = conf_zones[self.data_id]["cameras"]
		zone_no = 0
		for keys in zone_info.keys():
			if str(self.threadid) in keys :
				zone_no=keys

		zone_no = int(zone_no)
		connection = False
		camera = cv2.VideoCapture(self.cam_url)
		start = time.time()
		firstFrame = None

		while(not connection):
			try:
				_, frame = camera.read()
				connection = True

			except:
				camera = cv2.VideoCapture(self.cam_url)
				print camera

		# loop over the frames of the video

		hnd_count = 0


		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+ "variables_hd.decision[zone_no]:" + str(variables_hd.decision[zone_no])
		if variables_hd.decision[zone_no] == True:
			print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+"QUITTING YOLO" + "(Camera " + str(self.threadid) + ")"
			return

		(grabbed, frame) = camera.read()

		if grabbed is None:
			print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Waiting"

		cv2.imwrite(conf["img_src"],frame)
		FNULL = open(os.devnull, 'w')
		hp=subprocess.call(["sh", "/home/stark/BA/yolo_dev/darknet_classroom/darknet/yolounit.sh"],stdout=FNULL, stderr=subprocess.STDOUT)
		print "No of Occupants(YOLO):" + str(hp)

		if hp>=1:
			logging.info('Mutex Acquired, Camera:' + str(self.threadid +1))
			logging.info('Yolo HD, Camera:' + str(self.threadid +1))
			variables_hd.mutex.acquire()
			variables_hd.decision[zone_no] = True;
			send_HD(self.data_id,self.cycle,zone_no)
			print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+"Camera " + str(self.threadid) + ":Yolo HD," + str(hp) + "People Detected"
			variables_hd.mutex.release()
			logging.info('Mutex Released, Camera:' + str(self.threadid +1))
			camera.release()
			#cv2.destroyAllWindows()
			print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "HUMAN PRESENCE by yolo:" + str(variables_hd.hd_zone[zone_no])
			return

		if hnd_count < conf["no_of_HNDS"]:
			hnd_count+=1


		if conf["show_video"]:
			cv2.imread(conf["img_result"],frame)
			cv2.imshow("Human Presence", frame)

		#key = cv2.waitKey(1) & 0xFF
		camera.release()
		#cv2.destroyAllWindows()
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "Human Presence by yolo:" + str(variables_hd.hd_zone[zone_no])
		variables_hd.hd_zone[zone_no] = False
		return
