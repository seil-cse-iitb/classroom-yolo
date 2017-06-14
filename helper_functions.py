import MySQLdb as mdb
import sys

# ADD LO
def connect_to_database(conf):

    '''
    Connects to the Database datapool and retrieves the ip and port from data forwarder info table
    '''
    db_ip = conf["db_ip"]
    database = conf["database"]
    username = conf["username"]
    password = conf["password"]

    con = mdb.connect(db_ip , username , password , database)
    cur = con.cursor()
    cur.execute("select ip,port from data_forwarder_info;")
    row = cur.fetchone()
    pr1_ip = str(row[0])
    pr1_port = int(row[1])
    row = cur.fetchone()
    pr2_ip = str(row[0])
    pr2_port = int(row[1])
    con.close()
    return pr1_ip, pr1_port, pr2_ip, pr2_port
