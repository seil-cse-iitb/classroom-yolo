import time
import numpy as np
import cv2
import json
import threading
from hd_variables import variables_hd
from datetime import datetime
import subprocess
from workerprocess_class import *

class run_yolo(threading.Thread):

	def __init__(self,roomno,cam_url,threadid):
		threading.Thread.__init__(self)
		self.threadid = threadid
		self.cam_url = cam_url
		self.roomno = roomno

	def run(self):
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Starting YOLO for Camera " + str(self.threadid+1)
		HD=False
		conf = json.load(open('config_imageprocessing.json'))

		conf_zones = json.load(open('config_zones.json'))

		zone_info = conf_zones[self.roomno]["cameras"]
		for keys in zone_info.keys():
			if str(self.threadid) in keys :
				zone_no=keys

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

		while True:

			if variables_hd.decision[zone_no] == True:
				return

			(grabbed, frame) = camera.read()

			if grabbed is None:
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Waiting"
				continue

			cv2.imwrite(conf["img_src"],frame)
			hp=subprocess.call(["./darknet","detect","cfg/yolo.cfg","yolo.weights","data/find_hp.jpg"])

			if hp==1:
				variables_hd.mutex.acquire()
				variables_hd.Decision[zone_no] = True;
				send_HD(zone_no)
				variables_hd.mutex.release()
				variables_hd.hd_zone[zone_no] = True
				camera.release()
				#cv2.destroyAllWindows()
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "HUMAN PRESENCE:" + str(variables_hd.hd_zone[zone_no])
				return

			if hnd_count < conf["no_of_HNDS"]:
				hnd_count+=1


			if conf["show_result"]:
				cv2.imread(conf["img_result"],frame)
				cv2.imshow("Human Presence", frame)

			#key = cv2.waitKey(1) & 0xFF
		camera.release()
		#cv2.destroyAllWindows()
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "Human Presence:" + str(variables_hd.hd_zone[zone_no])
		variables_hd.hd_zone[zone_no] = False
		return
