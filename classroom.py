'''
This code is the server code for the SCC.
It receives PIR trigger messages, triggers the camera,
processes the camera feed and sends the output (HD/HND) vis Ethernet.
'''
import json
import sys
from helper_functions import connect_to_database
from workerprocess_class import WorkerProcess
from threading import Lock
from  hd_variables import variables_hd
def main():
    print "Starting...."

    variables_hd.mutex = Lock()
    conf = json.load(open("config_main.json"))

    pr1_ip, pr1_port, pr2_ip, pr2_port = connect_to_database(conf)

    try:
        roomno = sys.argv[1]
        variables_hd.roomno=roomno
        _ = tuple(conf[roomno])

    except:
        sys.exit("Invalid/No Room Number passed as an argument")

    data_id = conf[roomno]["data_id"]
    port_no = conf[roomno]["port_no"]
    cam_urls = conf[roomno]["camera_urls"]
    #print data_id, port_no, cam_urls

    pool = []

    #help:def __init__(self, data_id, cam_urls, port, pr1_ip, pr1_port, pr2_ip ,pr2_port):
    pool.append(WorkerProcess(roomno,data_id, port_no, cam_urls, pr1_ip, pr1_port, pr2_ip, pr2_port))

    # Start all process
    for process in pool:
        process.start()

    # wait for process to die
    for process in pool:
        process.join()


if __name__ == "__main__":
    main()
