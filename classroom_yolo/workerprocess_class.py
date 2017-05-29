from threading import Event , Thread
import multiprocessing
import socket
import time
import cv2
import json
from runyolo import run_yolo
from networkLayer import msg_recived,msg_send,createSocket
from hd_variables import variables_hd
from datetime import datetime

class WorkerProcess(multiprocessing.Process):

    def __init__(self, roomno, data_id, port, cam_urls, pr1_ip, pr1_port, pr2_ip ,pr2_port):

        super(WorkerProcess, self).__init__()
        self.conf = json.load(open('config_imageprocessing.json'))
        self.conf_zonal = json.load(open('config_zones.json'))

        self.roomno=roomno
        self.port=port
        self.data_id = data_id
        self.no_of_zones = self.conf_zonal[self.data_id]["no_of_zones"]
        self.cam_urls = []
        #self.HD = []
        self.HD_zones = []

        for i in range(len(cam_urls)):
            self.cam_urls.append(cam_urls[i])
            #self.HD.append(False)

        for i in range(self.no_of_zones):
            self.HD_zones.append(False)

        self.cycle = Event()
        self.msg_recv = ""
        self.zonalcheck = self.conf["zonalcheck"]
        self.checkafterHND = self.conf["checkafterHND"]
        self.ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        self.HD_overall = False
        self.T_Restart = self.conf["T_Restart"]
        self.T_standby = self.conf["T_standby"]
        self.startmain = time.time()
        self.temp = ""
        createSocket(self.port)

    def send_HD(self,zone_no):
        if self.cycle.is_set():
            reply_msg = "#" + self.data_id + "I" + str(zone_no+1) + ","
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Cycle status " , self.cycle.is_set()
            reply_msg += "HD;"
            msg_send(reply_msg)
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(self.HD_zones[zone_no])

            if zone_no==1:
                self.zonalcheck = self.conf["zonalcheck"]
                print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" RESETTING ZONAL CHECK:" + str(self.zonalcheck)


    def send_HND(self,zone_no):
        reply_msg = "#" + self.data_id + "I" + str(zone_no+1) + ","
        reply_msg += "HND;"
        msg_send(reply_msg)
        print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(self.HD_zones[zone_no])
        time.sleep(1)

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
                time.sleep(self.T_standby)
                self.HD_overall = False
                self.HD_Face = False

                print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" %s Cameras in the Room" %len(self.cam_urls)

                threads = []
                #face_detection(self.cam_urls[0])

                for i in range(len(self.cam_urls)):
                    this_thread = run_yolo(self.cam_urls[i],i,self.roomno)
                    threads.append(this_thread)
                    this_thread.start()

                # FIX THIS!!! (But even if I don't hard code the values, I'll still be hard coding the method of ZO. SIgh)

                for t in threads:
                    t.join()

                #chehking for zonal is true or false
                if self.conf_zonal[self.data_id]["zonal"]:
                    self.HD_zones[0] = variables_hd.cam_url_hd[0] or variables_hd.cam_url_hd[2]
                    self.HD_zones[1] = variables_hd.cam_url_hd[1]

                else:
                    self.HD_zones[0] = variables_hd.cam_url_hd[0] or variables_hd.cam_url_hd[1] or variables_hd.cam_url_hd[2]

                    if len(self.HD_zones)>1:
                        self.HD_zones[1] = self.HD_zones[0]


                for i in range(self.no_of_zones):

                    if(not self.HD_zones[i]):
                        self.send_HND(i)

                    else:
                        self.send_HD(i)

                #checkafterHND is to check for motion after all appliances have been turned off in a class
                #if motion is not found checkafterHND times, algorithm is stopped until PIR is triggered

                for i in range(self.no_of_zones):
                    self.HD_overall = self.HD_overall or self.HD_zones[i]

                if (not self.HD_overall):

                    self.checkafterHND-=1
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Check after HND %s" % self.checkafterHND

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
