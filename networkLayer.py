'''
All the network related operations are done here
The message to/from the proxy forwarder are sent/recieved
'''

import sys
import socket
import json
import logging
from helper_functions import connect_to_database
from datetime import datetime
import time
from hd_variables import *

#ip and the port address to where the message has to be sent is pr2_ip, pr2_port
#pr1_ip, pr1_port are not used
conf = json.load(open('config_main.json'))
pr1_ip, pr1_port, pr2_ip, pr2_port = connect_to_database(conf)

#sockets to sent and recieve messages
sock_recv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

#gets my ip address
ip_own = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 80)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]


def createSocket(port):
    print "I'm " + str(ip_own)+"  on "+str(port)+" will be sending messages to " +str(pr2_ip)+" on "+str(pr2_port)
    sock_recv.bind((ip_own ,port))

def send_HD(data_id,cycle,zone_no):

    logging.info("Inside send_HD,"+'cycle:'+str(cycle.is_set)+'zone_no:'+str(zone_no))
    if cycle.is_set():

        reply_msg = "#" + data_id + "I" + str(zone_no+1) + ","
        print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Cycle status " , cycle.is_set()
        reply_msg += "HD;"
        msg_send(reply_msg)
        print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(variables_hd.hd_zone[zone_no])

def send_HND(data_id,zone_no):
    logging.info("Inside send_HD,"+'zone_no:'+str(zone_no))
    reply_msg = "#" + data_id + "I" + str(zone_no+1) + ","
    reply_msg += "HND;"
    msg_send(reply_msg)
    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Zone " + str(zone_no+1) + ":" + str(variables_hd.hd_zone[zone_no])
    time.sleep(1)


def msg_recived():
    msg=sock_recv.recv(1024)
    print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Message Recived : "+msg
    return msg

def msg_send(msg):
    flag_p1 = 0
    while flag_p1 >= 0:
        try:
            sock_send.sendto(msg , (pr2_ip,pr2_port))
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Message Sent : "+msg
            if msg[-3:-1] =='HD': #reduce processing load on Server
                time.sleep(5) #needs to be added to config file
            flag_p1 = -1

        except:
            flag_p1 += 1
            print datetime.now().strftime('[%d-%b-%y %H:%M:%S]')+" Network Error " , sys.exc_info()[0]
            print flag_p1 , " unable to send msg, retrying send action " , msg , " " , pr2_ip , " " , pr2_port
            continue
