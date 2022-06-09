from flask import Flask, jsonify, request, make_response
from flask_restful import Resource
import datetime

import manageDB, manageOTP, manageFCM


class Login_Locker(Resource):
	def post(self):
		lockername=str(request.json["lockername"])
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		id=str(request.json["id"])
		pw=str(request.json["pw"])
		print(lockername, id)
		checkOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		if checkOTP==-1: #사물함 정보가 존재하지 않을 경우
			print("Locker is not registered...")
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		elif checkOTP==-2:
			print("OTP timeout...")
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		elif checkOTP==0: # 사물함 OTP가 일치하지 않을 경우
			print("Locker OTP not match...")
			result={"result":"otp error"}
			return make_response(jsonify(result), 200)
		sql="SELECT id, name FROM client WHERE id='"+id+"' AND pw=password('"+pw+"');"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			sql="SELECT id FROM admin WHERE id='"+id+"' AND pw=password('"+pw+"');"
			manageDB.cur.execute(sql)
			row=manageDB.cur.fetchone()
			if row == None:
				print("Account not found...")
				result={"result":"id pw error"}
				return make_response(jsonify(result), 200)
			sql="UPDATE lockers SET signedID='"+id+"', status='waitOTP_admin' WHERE lockername='"+lockername+"';"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			result={"result":"success"}
			print('admin is trying to log in from locker:'+lockername)
			return make_response(jsonify(result), 200)
		sql="UPDATE lockers SET signedID='"+id+"', status='waitOTP' WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)


class Login_Locker_OTP(Resource):
	def post(self):
		ID=str(request.json["id"])
		lockername=str(request.json["lockername"])
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		clientotp=str(request.json["clientotp"])
		sql="SELECT otpKey, signedID, status, maxspaces, usedspaces FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		checkLockerOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		if checkLockerOTP == -1:
			print("Locker is not registered...")
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		elif checkLockerOTP == 0:
			print('locker otp doesn\'t match.')
			result={"result":"otp failed"}
			return make_response(jsonify(result), 200)
		elif checkLockerOTP == -2:
			print('locker otp timeout...')
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		if ID != str(row[1]) or ( str(row[2]) != "waitOTP" and str(row[2]) != "waitOTP_admin" ) :
			print("Access Denied......")
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		print('locker has been certificated.')

		if str(row[2]) == "waitOTP_admin":
			checkOTP=manageOTP.check_otp_for_admin(ID, clientotp)
			if checkOTP == 1:
				print('Admin OTP certificated.')
				sql="UPDATE lockers SET status='idle', signedID=NULL WHERE lockername='"+lockername+"';"
				manageDB.cur.execute(sql)
				manageDB.conn.commit()
				result={"result":"admin"}
				return make_response(jsonify(result), 200)

		checkOTP=manageOTP.check_otp_for_client(ID, clientotp)
		if checkOTP == 1:
			print('client OTP certificated.')
			sql="UPDATE lockers SET status='verified' WHERE lockername='"+lockername+"';"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			sql="SELECT status FROM client WHERE id='"+ID+"';"
			manageDB.cur.execute(sql)
			row2=manageDB.cur.fetchone()
			status=str(row2[0])
			if status == 'idle':
				result={"result":"idle", "maxspaces":int(row[3]), "usedspaces":int(row[4])}
				return make_response(jsonify(result), 200)
			elif status == 'reserved':
				sql="SELECT startdate FROM client WHERE id='"+ID+"';"
				manageDB.cur.execute(sql)
				row3=manageDB.cur.fetchone()
				startdate=datetime.datetime.strptime(str(row3[0]), '%Y-%m-%d')
				today=datetime.datetime.now()
				if today >= startdate:
					result={"result":"reserved", "isable":"true"}
				else:
					result={"result":"reserved", "isable":"false"}
				return make_response(jsonify(result), 200)
			elif status == 'using':
				sql="SELECT lockernum FROM "+lockername+" WHERE clientid='"+ID+"';"
				manageDB.cur.execute(sql)
				row4=manageDB.cur.fetchone()
				lockernum=int(row4[0])
				result={"result":"using", "lockernum":lockernum}
				return make_response(jsonify(result), 200)
			elif status == 'overdue':
				result={"result":"overdue"}
				return make_response(jsonify(result), 200)
		else:
			print('client OTP not match')
			result={"result":"otp failed"}
			return make_response(jsonify(result), 200)

class Oneday_Rent(Resource):
	def post(self):
		ID=str(request.json["id"])
		print(ID)
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		lockername=str(request.json["lockername"])
		sql="SELECT signedID, status, maxspaces, usedspaces FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		usedspaces = int(row[3])
		checkLockerOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		if checkLockerOTP != 1:
			print('locker otp doesn\'t match.')
			result={"result":"otp failed"}
			return make_response(jsonify(result), 200)
		if ID != str(row[0]) or str(row[1]) != "verified":
			print('Access denied...')
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		print('locker has been certificated.')
		today=datetime.datetime.today().strftime("%Y-%m-%d")
		usedspaces=int(row[3])
		maxspaces=int(row[2])
		lockernum=0
		i=1
		while i<=maxspaces:
			sql="SELECT lockernum FROM "+lockername+"  WHERE reserveddate='"+today+"' AND lockernum="+str(i)+";"
			manageDB.cur.execute(sql)
			row=manageDB.cur.fetchone()
			if row==None:
				sql="SELECT lockernum FROM "+lockername+" WHERE status=-1 AND lockernum="+str(i)+";"
				manageDB.cur.execute(sql)
				row=manageDB.cur.fetchone()
				if row == None:
					lockernum=i
					break
			i=i+1
		if lockernum==0:
			print('lockernum assignment error...')
			result={"result":"assignment error"}
			return make_response(jsonify(result), 200)

		sql="UPDATE client SET status='using', startdate='"+today+"', enddate='"+today+"', usinglockername='"+lockername+"'  WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="UPDATE lockers SET usedspaces="+str(usedspaces+1)+", signedID=NULL, status='idle' WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="INSERT INTO "+lockername+"(status, clientid, reserveddate, lockernum) VALUES(0, '"+ID+"','"+today+"',"+str(lockernum)+");"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success", "lockernum":lockernum}
		return make_response(jsonify(result), 200)

class Activate_Locker(Resource):
	def post(self):
		ID=str(request.json["id"])
		print(ID)
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		lockername=str(request.json["lockername"])
		sql="SELECT otpKey, signedID, status, maxspaces, usedspaces FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		maxspaces=int(row[3])
		checkLockerOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		sql="SELECT status FROM client WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		clientstatus=manageDB.cur.fetchone()
		if checkLockerOTP != 1:
			print('locker otp doesn\'t match.')
			result={"result":"otp failed"}
			return make_response(jsonify(result), 200)
		if ID != str(row[1]) or str(row[2]) != "verified":
			print('Access denied...')
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		if str(clientstatus[0]) != "reserved":
			print('not reserved...')
			result={"result":"not reserved"}
			return make_response(jsonify(result), 200)
		print('locker has been certificated.')
		usedspaces=int(row[4])
		lockernum=0
		i=1
		today=datetime.datetime.today().strftime("%Y-%m-%d")
		while i<=maxspaces:
			sql="SELECT lockernum FROM "+lockername+"  WHERE reserveddate='"+today+"' AND lockernum="+str(i)+";"
			manageDB.cur.execute(sql)
			row=manageDB.cur.fetchone()
			if row==None:
				sql="SELECT lockernum FROM "+lockername+" WHERE status=-1 AND lockernum="+str(i)+";"
				manageDB.cur.execute(sql)
				overduelist=manageDB.cur.fetchone()
				if overduelist==None:
					lockernum=i
					break
			i=i+1
		if lockernum==0:
			print('lockernum assignment error...')
			result={"result":"assignment error"}
			return make_response(jsonify(result), 200)
		sql="UPDATE client SET status='using' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="UPDATE "+lockername+" SET lockernum="+str(lockernum)+" WHERE clientid='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="UPDATE lockers SET signedID=NULL, status='idle', usedspaces="+str(usedspaces+1)+" WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="SELECT CAST(startdate AS CHAR), CAST(enddate AS CHAR) FROM client WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		startdate=str(row[0])
		enddate=str(row[1])
		result={"result":"success", "lockernum":lockernum, "startdate":startdate, "enddate":enddate}
		return make_response(jsonify(result), 200)

class Deactivate_Locker(Resource):
	def post(self):
		ID=str(request.json["id"])
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		lockername=str(request.json["lockername"])
		sql="SELECT otpKey, signedID, status, usedspaces FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		usedspaces=int(row[3])
		checkLockerOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		if checkLockerOTP != 1:
			print('locker otp doesn\'t match.')
			result={"result":"otp failed"}
			return make_response(jsonify(result), 200)
		if ID != str(row[1]) or str(row[2]) != "verified":
			print('Access denied...')
			result={"result":"denied"}
			return make_response(jsonify(result), 200)
		print('locker has been certificated.')
		sql="SELECT lockernum FROM "+lockername+" WHERE clientid='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		lockernum=int(row[0])
		sql="UPDATE client SET status='idle', startdate=NULL, enddate=NULL, usinglockername=NULL WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="UPDATE lockers SET usedspaces="+str(usedspaces-1)+", signedID=NULL, status='idle' WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="DELETE FROM "+lockername+" WHERE clientid='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success", "lockernum":lockernum}
		return make_response(jsonify(result), 200)


class Illegal_Open_Detected(Resource):
	def post(self):
		lockername=str(request.json["lockername"])
		lockernum=int(request.json["lockernum"])
		lockerotp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		sql="SELECT otpKey FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		checkLockerOTP=manageOTP.check_otp_for_locker(lockername, lockerotp, currtime)
		if checkLockerOTP != 1:
			print('locker otp doesn\'t match...')
			result={"result":"failed"}
			return make_response(jsonify(result), 200)
		now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql="INSERT INTO illegal_open_log(lockername, lockernum, time) VALUES('"+lockername+"', "+str(lockernum)+", '"+now+"');"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		manageFCM.notice_Illegal_Open(lockername, lockernum)
		result={"result":"success"}
		return make_response(jsonify(result), 200)


