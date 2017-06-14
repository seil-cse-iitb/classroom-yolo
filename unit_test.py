
#UNIT TESTING motion, face detection
from runyolo import run_yolo
from yolo_unittest import yolo_unittest

def main():

    print "Unit Testing.."
    cam_201_1 = "rtsp://10.129.23.230:554/ISAPI/streaming/channels/101?auth=YWRtaW46dGhlY2FtQHNlaWw="
    cam_201_2 = "rtsp://10.129.23.231:1024/ISAPI/streaming/channels/101?auth=YWRtaW46dGhlY2FtQHNlaWw="
    cam_201_3 = "rtsp://10.129.23.232:554/ISAPI/streaming/channels/101?auth=YWRtaW46dGhlY2FtQHNlaWw="

    #cam_205_1 = "rtsp://10.129.23.233:1024/ISAPI/streaming/channels/101?auth=YWRtaW46dGhlY2FtQHNlaWw="
    #cam_205_2 = "rtsp://10.129.23.234:554/ISAPI/streaming/channels/101?auth=YWRtaW46dGhlY2FtQHNlaWw="
    HD1 = yolo_unittest(cam_201_1)
    HD2 = yolo_unittest(cam_201_2)
    HD3 = yolo_unittest(cam_201_3)
    print "PRESENCE1" + str(HD1)
    print "PRESENCE2" + str(HD2)
    print "PRESENCE3" + str(HD3)
    HD =  HD1 or HD2 or HD3
    print "Overall Presence: " + str(HD)

if __name__ == "__main__":
    main()
