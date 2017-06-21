from threading import Event , Thread
import multiprocessing
import socket
import time
import cv2
import json
import logging
from runyolo import run_yolo
from networkLayer import msg_recived,msg_send,send_HND,createSocket
from hd_variables import variables_hd
from datetime import datetime
from motiondetection import motiondetection

class WorkerProcess(multiprocessing.Process):
    def __init__(self, roomno,data_id, port, cam_urls, pr1_ip, pr1_port, pr2_ip ,pr2_port):

        #logging.info("WorkerProcess Initialization Started")

        self.conf= json.load(open('config_imageprocessing.json'))
        self.conf_zonal = json.load(open('config_zones.json'))
        super(WorkerProcess, self).__init__()
        self.roomno = roomno
        self.port=port
        self.data_id = data_id
        self.no_of_zones = self.conf_zonal[data_id]["no_of_zones"]
        self.cam_urls = []
        #HD = []

        #SELF.HD_ZONES SHOULD BE REMOVED
        self.HD_zones = []

        for i in range(len(cam_urls)):
            self.cam_urls.append(cam_urls[i])
            #HD.append(False)
        self.cycle = Event()
        self.msg_recv = ""
        #zonalcheck = self.conf["zonalcheck"]
        self.checkafterHND = self.conf["checkafterHND"]
        self.ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        self.HD_overall = False
        self.T_standby = self.conf["T_standby"]
        self.temp = ""
        createSocket(port)
        #logging.info("WorkerProcess Initialization Ended")

    def run(self):
        self.cycle.clear()
        t1 = Thread(target = self.state_control)
        t1.start()

        while True:

            self.cycle.wait()
            data = self.msg_recv

            if not self.HD_overall:

                if data[0] == "#" and data[-1] == ";":
                    temp = data[1:-1].split(",")

            if temp[1] == "T":
                data = 'reset'
                #WHY ARE WE SLEEPING
                time.sleep(self.T_standby)
                self.HD_overall = False

                print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" %s Cameras in the Room" %len(self.cam_urls)

                threads = []
                #face_detection(cam_urls[0])

                for i in range(len(self.cam_urls)):
                    yolo_thread = run_yolo(self.cycle,self.data_id,self.cam_urls[i],i)
                    threads.append(yolo_thread)
                    yolo_thread.start()
                    motion_detection_thread =motiondetection(self.cycle,self.data_id,self.cam_urls[i],i)
                    threads.append(motion_detection_thread)
                    motion_detection_thread.start()


                # FIX THIS!!! (But even if I don't hard code the values, I'll still be hard coding the method of ZO. SIgh)

                for t in threads:
                    t.join()


                for i in range(self.no_of_zones):
                    if variables_hd.decision[i] == False:
                        send_HND(self.data_id,i)
                    variables_hd.decision[i] = False

                #checkafterHND is to check for motion after all appliances have been turned off in a class
                #if motion is not found checkafterHND times, algorithm is stopped until PIR is triggered

                for i in range(self.no_of_zones):
                    self.HD_overall = self.HD_overall or variables_hd.hd_zone[i]

                logging.info('Overall Human Presence:' + str(self.HD_overall))

                if (not self.HD_overall):

                    self.checkafterHND-=1
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Check after HND %s" % self.checkafterHND
                    logging.info('Check After HND:' + str(self.checkafterHND))

                    if self.checkafterHND>0:
                        continue

                    else:
                        self.cycle.clear()

    def state_control(self):

        while True:

            self.msg_recv = msg_recived()

            if self.msg_recv[0] == "#" and self.msg_recv[-1] == ";":
                temp = self.msg_recv[1:-1].split(",")

                if temp[1] == "Init":
                    self.cycle.clear()
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" INIT MESSAGE RECEIVED"

                elif temp[1] == "T":
                    self.cycle.set()
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" PIR TRUE RECEIVED"
                    self.checkafterHND = self.conf["checkafterHND"]
