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
from motiondetection import motiondetection


class WorkerProcess(multiprocessing.Process):
    def __init__(self, roomno,data_id, port, cam_urls, pr1_ip, pr1_port, pr2_ip ,pr2_port):

        conf= json.load(open('config_imageprocessing.json'))
        conf_zonal = json.load(open('config_zones.json'))
        super(WorkerProcess, self).__init__()
        roomno = roomno
        port=port
        data_id = data_id
        no_of_zones = conf_zonal[data_id]["no_of_zones"]
        cam_urls = []
        #HD = []

        #SELF.HD_ZONES SHOULD BE REMOVED
        HD_zones = []

        for i in range(len(cam_urls)):
            cam_urls.append(cam_urls[i])
            #HD.append(False)

        #SELF.HD_ZONES SHOULD BE REMOVED
        for i in range(no_of_zones):
            HD_zones.append(False)


        msg_recv = ""
        #zonalcheck = conf["zonalcheck"]
        checkafterHND = conf["checkafterHND"]
        ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        HD_overall = False
        T_standby = conf["T_standby"]
        temp = ""
        Decision=False

        createSocket(port)

    def send_HD(zone_no):
        if cycle.is_set():
            reply_msg = "#" + data_id + "I" + str(zone_no+1) + ","
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Cycle status " , cycle.is_set()
            reply_msg += "HD;"
            msg_send(reply_msg)
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(HD_zones[zone_no])

            if zone_no==1:
                zonalcheck = conf["zonalcheck"]
                print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" RESETTING ZONAL CHECK:" + str(zonalcheck)


    def send_HND(zone_no):
        reply_msg = "#" + data_id + "I" + str(zone_no+1) + ","
        reply_msg += "HND;"
        msg_send(reply_msg)
        print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(HD_zones[zone_no])
        time.sleep(1)


    def state_control(self):

        while True:

            msg_recv = msg_recived()

            if msg_recv[0] == "#" and msg_recv[-1] == ";":
                temp = msg_recv[1:-1].split(",")

                if temp[1] == "Init":
                    cycle.clear()
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" INIT MESSAGE RECEIVED"

                elif temp[1] == "T":
                    cycle.set()
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" PIR TRUE RECEIVED"
                    checkafterHND = conf["checkafterHND"]


                    

    def run(self):
        cycle = Event()
        cycle.clear()
        t1 = Thread(target = state_control)
        t1.start()

        while True:

            cycle.wait()
            data = msg_recv

            if not HD_overall:

                if data[0] == "#" and data[-1] == ";":
                    temp = data[1:-1].split(",")

            if temp[1] == "T":
                data = 'reset'
                #WHY ARE WE SLEEPING
                time.sleep(T_standby)
                HD_overall = False
                HD_Face = False

                print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" %s Cameras in the Room" %len(cam_urls)

                threads = []
                #face_detection(cam_urls[0])

                for i in range(len(cam_urls)):
                    yolo_thread = run_yolo(roomno,cam_urls[i],i)
                    threads.append(yolo_thread)
                    yolo_thread.start()
                    motion_detection_thread =motion_detection(roomno,cam_urls[i],i)
                    threads.append(motion_detection_thread)
                    motion_detection_thread.start()


                # FIX THIS!!! (But even if I don't hard code the values, I'll still be hard coding the method of ZO. SIgh)

                for t in threads:
                    t.join()


                for i in range(len(no_of_zones)):
                    if variables_hd.decision[i] == False:
                        send_HND(i)
                    variables_hd.decision[i] = False

                #checkafterHND is to check for motion after all appliances have been turned off in a class
                #if motion is not found checkafterHND times, algorithm is stopped until PIR is triggered

                for i in range(no_of_zones):
                    HD_overall = HD_overall or HD_zones[i]

                if (not HD_overall):

                    checkafterHND-=1
                    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Check after HND %s" % checkafterHND

                    if checkafterHND>0:
                        continue

                    else:
                        cycle.clear()
