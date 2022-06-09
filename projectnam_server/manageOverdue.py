from flask import Flask, jsonify, request, make_response
from flask_restful import Resource
from checkLoginToken import *

import manageDB
import schedule, threading, time, datetime
import manageFCM

def setUsedspaces():
	sql="SELECT lockername FROM lockers"
	manageDB.cur.execute(sql)
	lockers=manageDB.cur.fetchall()
	lockers_count=len(lockers)
	for i in range(lockers_count):
		lockername=str(lockers[i][0])
		sql="SELECT COUNT(*) FROM "+lockername+" WHERE UNIX_TIMESTAMP(CAST(reserveddate AS DATE)) = UNIX_TIMESTAMP(CAST(NOW() AS DATE));"
		manageDB.cur.execute(sql)
		usedspace=int(manageDB.cur.fetchone()[0])
		sql="SELECT clientid FROM "+lockername+" WHERE status=-1 GROUP BY clientid;"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchall()
		overdue_length=len(row)
		usedspace+=overdue_length
		sql="UPDATE lockers SET usedspaces="+str(usedspace)+" WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
	print('setting usedspaces done.')


def checkOverdue():
	print('Beginning of check overdue...')
	sql="SELECT id, usinglockername FROM client WHERE UNIX_TIMESTAMP(CAST(enddate AS DATE)) <= UNIX_TIMESTAMP(CAST(NOW()-INTERVAL 1 DAY AS DATE));"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	row_length=len(row)
	print('overdue people count : '+str(row_length))
	i=0
	isPushedToAdmin={}
	for i in range(row_length):
		ID=str(row[i][0])
		lockername=str(row[i][1])
		sql="SELECT lockernum, status FROM "+lockername+" WHERE clientid='"+ID+"';"
		manageDB.cur.execute(sql)
		reserveData=manageDB.cur.fetchone()
		lockernum=int(reserveData[0])
		status=int(reserveData[1])
		print('#'+str(i+1)+' overdue ID : '+ID+', lockername : '+lockername+', lockernum : '+str(lockernum)+', status : '+str(status))
		sql="UPDATE client SET status='overdue' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		if status == 0 :
			sql="UPDATE "+lockername+" SET status=-1 WHERE clientid='"+ID+"' AND status=0;"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			sql="SELECT name, email, CAST(startdate AS CHAR), CAST(enddate AS CHAR) FROM client WHERE id='"+ID+"';"
			manageDB.cur.execute(sql)
			info=manageDB.cur.fetchone()
			name=str(info[0])
			email=str(info[1])
			startdate=str(info[2])
			enddate=str(info[3])
			sql="INSERT INTO overdue_log(num, name, id, email, lockername, lockernum, startdate, enddate, iscollected) VALUES(NULL, '"+name+"', '"+ID+"', '"+email+"', '"+lockername+"', "+str(lockernum)+", '"+startdate+"', '"+enddate+"', 'false');"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
		if status==-2 :
			print('skip push')
		elif lockername not in isPushedToAdmin :
			sql="SELECT id FROM admin WHERE lockername='"+lockername+"';"
			manageDB.cur.execute(sql)
			adminlist=manageDB.cur.fetchall()
			admin_length=len(adminlist)
			print('adminlist:')
			print(adminlist)
			for j in range(admin_length):
				print('getadmin:'+str(adminlist[j][0]))
				sql="SELECT token FROM firebasetoken WHERE id='"+str(adminlist[j][0])+"';"
				manageDB.cur.execute(sql)
				fetchobject=manageDB.cur.fetchone()
				if fetchobject != None:
					fcmtoken=str(fetchobject[0])
					manageFCM.noticeOverdue_admin(fcmtoken, lockername)
					print('Pushed to admin : '+str(adminlist[j][0]))
			isPushedToAdmin[lockername]=1
	print('Checking overdue done.')
	setUsedspaces()

def noticeOverdue_Client():
	print('Beginning of notice overdue to client...')
	sql="SELECT id, usinglockername FROM client WHERE status='overdue';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	row_length=len(row)
	print("Overdue clients : "+str(row_length))
	for i in range(row_length):
		ID=str(row[i][0])
		lockername=str(row[i][1])
		sql="SELECT token FROM firebasetoken WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		fcmtoken=str(manageDB.cur.fetchone()[0])
		manageFCM.noticeOverdue_client(fcmtoken, lockername)
		print('Pushed to client : '+ID)
	print('Notice overdue done.')

def setOverdue():
	checkOverdue()
	noticeOverdue_Client()

setOverdue()

schedule.every().day.at("00:10").do(checkOverdue)
schedule.every().day.at("08:00").do(noticeOverdue_Client)

def scheduledOverdue(step):
	while True:
		schedule.run_pending()
		time.sleep(step)

overduethread = threading.Thread(target=scheduledOverdue, args=(1,))
overduethread.daemon = True
overduethread.start()



class Load_Overdue_List(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT lockername FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		lockername=str(manageDB.cur.fetchone()[0])
		sql="SELECT num, name, id, email, lockernum, CAST(startdate AS CHAR), CAST(enddate AS CHAR), iscollected, CAST(returntime AS CHAR) FROM overdue_log WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchall()
		length=len(row)
		result={}
		result['length']=length
		for i in range(length):
			result['num'+str(i)]=int(row[i][0])
			result['name'+str(i)]=str(row[i][1])
			result['id'+str(i)]=str(row[i][2])
			result['email'+str(i)]=str(row[i][3])
			result['lockernum'+str(i)]=int(row[i][4])
			result['startdate'+str(i)]=str(row[i][5])
			result['enddate'+str(i)]=str(row[i][6])
			result['iscollected'+str(i)]=str(row[i][7])
			if row[i][8] is not None:
				result['returntime'+str(i)]=str(row[i][8])
			else:
				result['returntime'+str(i)]="none"
		result['result']="success"
		return make_response(jsonify(result), 200)

class Collect_Overdue_Storage(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		num=int(request.json["num"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT * FROM overdue_log WHERE num="+str(num)+";"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		clientid=str(row[2])
		lockername=str(row[4])
		sql="UPDATE "+lockername+" SET status=-2 WHERE clientid='"+clientid+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		print("collect num \#" + str(num))
		sql="UPDATE overdue_log SET iscollected='true' WHERE num="+str(num)+";"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		setUsedspaces()
		return make_response(jsonify(result), 200)

class Return_Overdue_Storage(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		num=int(request.json["num"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT * FROM overdue_log WHERE num="+str(num)+";"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		clientid=str(row[2])
		lockername=str(row[4])
		iscollected=str(row[8])
		if iscollected != "true":
			print("storage not collected...")
			result={"result":"not collected"}
			return make_response(jsonify(result), 200)
		sql="DELETE FROM "+lockername+" WHERE clientid='"+clientid+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		now=datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
		sql="UPDATE overdue_log SET iscollected='true', returntime='"+now+"' WHERE num="+str(num)+";"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success", "returntime":now}
		sql="UPDATE client SET status='idle', startdate=NULL, enddate=NULL, usinglockername=NULL WHERE id='"+clientid+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		return make_response(jsonify(result), 200)
