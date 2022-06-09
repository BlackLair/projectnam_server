from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, reqparse



import time

import json

import manageDB
import manageOTP

class Connect_Locker(Resource):
	def post(self):
		lockername=str(request.json["lockername"])
		IP=str(request.remote_addr)
		sql="SELECT lockername FROM lockers WHERE lockername = '"+lockername+"';"
		manageDB.cur.execute(sql)
		print("lockername : "+lockername+", IP : "+IP+"';")
		row=manageDB.cur.fetchone()
		if row == None : #해당되는 사물함 db가 없을 경우 ( 새 사물함일 경우 )
			location=str(request.json["location"])
			maxspaces=int(request.json["maxspaces"])
			sql="CREATE TABLE "+lockername+" ( num INT PRIMARY KEY AUTO_INCREMENT, status INT, clientid TEXT, reserveddate DATE, lockernum INT);"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			otpkeyb32=manageOTP.generate_otp_key()
			time.sleep(0.5)
			while True:
				randomString=manageOTP.generate_otp_key()
				lockercode=randomString[0:8]
				sql="SELECT lockercode FROM lockers WHERE lockercode='"+lockercode+"';"
				manageDB.cur.execute(sql)
				row=manageDB.cur.fetchone()
				if row==None:
					break
			sql="INSERT INTO lockers VALUES('"+lockername+"','"+location+"','"+IP+"','"+otpkeyb32+"',"+str(maxspaces)+",0, '0', '0',password('"+lockercode+"'));"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			time.sleep(1)
			result={"result":"success", "otpkey":otpkeyb32, "lockercode":lockercode}
			print('new locker registered.')
			return make_response(jsonify(result), 200)
		otp=str(request.json["otp"])
		currtime=str(request.json["currtime"])
		result=manageOTP.check_otp_for_locker(lockername, otp, currtime)
		if result==1:
			sql="UPDATE lockers SET ip='"+IP+"' WHERE lockername='"+lockername+"';"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			result={"result":"success"}
			print('otp match.')
			return make_response(jsonify(result), 200)
		else:
			print('otp doesn\'t match.')
			result={"result":"failed"}
			return make_response(jsonify(result), 200)
