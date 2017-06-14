import time
import numpy as np
import cv2
import json
import threading
from hd_variables import variables_hd
from datetime import datetime
import subprocess

def yolo_unittest(cam_url):
    HD=False
    conf = json.load(open('config_imageprocessing.json'))
    HD_Timer =0
    connection = False
    camera = cv2.VideoCapture(cam_url)
    start = time.time()
    firstFrame = None

    while(not connection):
    	try:
    		_, frame = camera.read()
    		connection = True

    	except:
    		camera = cv2.VideoCapture(cam_url)
    		print camera

    # loop over the frames of the video

    hnd_count = 0

    while True:

    	(grabbed, frame) = camera.read()

    	if grabbed is None:
    		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Waiting"
    		continue

    	cv2.imwrite("/home/malvika/darknet_classroom/darknet/data/find_hp.jpg",frame)
    	hp=subprocess.call(["sh", "/home/malvika/darknet_classroom/darknet/yolounit.sh"])

    	if hp==1:
    		HD = True
    		camera.release()
    		#cv2.destroyAllWindows()
    		print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Camera "+ "HUMAN PRESENCE:" + str(HD)
    		#variables_hd.hd_zone[self.threadid] = HD
    		return HD

    	if hnd_count < conf["no_of_HNDS"]:
    		hnd_count+=1

        else:
            HD = False
            camera.release()
            #cv2.destroyAllWindows()
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+ "Human Presence:" + str(HD)
            return HD
            #variables_hd.hd_zone[self.threadid] = HD


    	if conf["show_result"]:
    		cv2.imread("/home/malvika/darknet_classroom/darknet/predictions.png",frame)
    		cv2.imshow("Human Presence", frame)

    	#key = cv2.waitKey(1) & 0xFF

    return
