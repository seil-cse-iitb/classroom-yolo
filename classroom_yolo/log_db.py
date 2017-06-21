from datetime import datetime
from MySQLdb import *
def write_to_mysql(classroom,count):
	ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        con = connect("10.129.23.161","writer","datapool","datapool")
        cur = con.cursor()
        
        sql  = "insert into yolo_log(TS,COUNT,CID) values ('%s','%d','%s')" %(ts,count,classroom)
        print sql
        try:
                print "Executing sql"
                cur.execute(sql)
                print "Executed sql"
                con.commit()
                print "Commit -- Done"
        except:
                con.rollback()
                print "Execution failed -- Rollback in progress.."
        con.close()

#write_mysql("201",10)
