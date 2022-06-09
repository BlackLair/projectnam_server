import time, datetime

from flask import Flask, jsonify, request, make_response
from flask_restful import Resource
import json
import manageDB, manageEmail
from checkLoginToken import *


class Load_locker_status(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT lockername FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		lockername=str(row[0])
		sql="SELECT maxspaces FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		maxspaces=int(row[0])
		today=datetime.datetime.today().strftime("%Y-%m-%d")
		result={}
		for i in range(1, maxspaces+1):
			sql="SELECT clientid FROM "+lockername+" WHERE reserveddate='"+today+"' AND lockernum="+str(i)+";"
			manageDB.cur.execute(sql)
			row=manageDB.cur.fetchone()
			if row != None:
				sql="SELECT status FROM client WHERE id='"+str(row[0])+"';"
				manageDB.cur.execute(sql)
				status=str(manageDB.cur.fetchone()[0])
				result['#'+str(i)]=status
			else:
				sql="SELECT clientid FROM "+lockername+" WHERE lockernum="+str(i)+" AND status=-1;"
				manageDB.cur.execute(sql)
				overduelist=manageDB.cur.fetchone()
				if overduelist!=None:
					result['#'+str(i)]="overdue"
				else:
					result['#'+str(i)]="idle"
		result['result']="success"
		result['length']=maxspaces
		return make_response(jsonify(result), 200)


class Load_locker_details(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		lockernum=int(request.json["lockernum"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		today=datetime.datetime.today().strftime("%Y-%m-%d")
		sql="SELECT lockername FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		lockername=str(manageDB.cur.fetchone()[0])
		sql="SELECT clientid FROM "+lockername+" WHERE lockernum="+str(lockernum)+" AND reserveddate='"+today+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		sql="SELECT clientid FROM "+lockername+" WHERE lockernum="+str(lockernum)+" AND status=-1;"
		manageDB.cur.execute(sql)
		overdue=manageDB.cur.fetchone()
		if row != None or overdue != None:
			if row != None:
				clientID=row[0]
			else:
				clientID=overdue[0]
			sql="SELECT email, status, DATE_FORMAT(startdate, '%Y-%m-%d'), DATE_FORMAT(enddate, '%Y-%m-%d'), name FROM client WHERE id='"+clientID+"';"
			manageDB.cur.execute(sql)
			row=manageDB.cur.fetchone()
			email=str(row[0])
			status=str(row[1])
			startdate=str(row[2])
			enddate=str(row[3])
			name=str(row[4])
			print('status:'+status)
			result={"result":"success", "id":clientID, "email":email, "status":status, "startdate":startdate, "enddate":enddate, "name":name}
			return make_response(jsonify(result), 200)
		else:
			print('status:idle')
			result={"result":"success", "status":"idle"}
			return make_response(jsonify(result), 200)



class Load_Illegal_Open_History(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print("token not match...")
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT lockername FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		lockername=str(row[0])
		sql="SELECT * FROM illegal_open_log WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchall()
		length=len(row)
		result={}
		result['length']=length
		for i in range(length):
			result['num'+str(i)]=int(row[i][0])
			result['time'+str(i)]=str(row[i][3])
			result['lockernum'+str(i)]=int(row[i][2])
		result['result']="success"
		return make_response(jsonify(result), 200)

