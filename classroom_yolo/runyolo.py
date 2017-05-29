import time
import numpy as np
import cv2
import json
import threading
from hd_variables import variables_hd
from datetime import datetime
import subprocess

from log_db import write_to_mysql

class run_yolo(threading.Thread):

	def __init__(self,cam_url,threadid,roomno):
		threading.Thread.__init__(self)
		self.threadid = threadid
		self.cam_url = cam_url
		self.roomno = roomno

	def run(self):
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Starting Motion Detection for Camera " + str(self.threadid+1)
		HD=False
		conf = json.load(open('config_imageprocessing.json'))
		HD_Timer =0
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

			(grabbed, frame) = camera.read()

			if grabbed is None:
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Waiting"
				continue

			cv2.imwrite("/home/stark/Desktop/darknet_classroom/darknet/data/find_hp.jpg",frame)
			hp=subprocess.call(["sh", "/home/stark/Desktop/darknet_classroom/darknet/yolounit.sh"])

			write_to_mysql(self.roomno,hp)
			if hp>0:
				HD = True
				camera.release()
				#cv2.destroyAllWindows()
				print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "HUMAN PRESENCE:" + str(HD)
				variables_hd.cam_url_hd[self.threadid] = HD
				return

			if hnd_count < conf["no_of_HNDS"]:
				hnd_count+=1

			else:
				HD = False
            			camera.release()
            			#cv2.destroyAllWindows()
            			print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+ "Human Presence:" + str(HD)
            			variables_hd.cam_url_hd[self.threadid] = HD
				return

			if conf["show_result"]:
				cv2.imread("/home/stark/Desktop/darknet_classroom/darknet/predictions.png",frame)
				cv2.imshow("Human Presence", frame)

			#key = cv2.waitKey(1) & 0xFF

		camera.release()
		#cv2.destroyAllWindows()
		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ str(self.threadid+1) + "Human Presence:" + str(HD)
		variables_hd.cam_url_hd[self.threadid] = HD
		return
