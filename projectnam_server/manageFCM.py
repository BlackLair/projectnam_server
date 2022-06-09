from flask import Flask, jsonify, request, make_response
from flask_restful import Resource

import manageDB
from checkLoginToken import *

import datetime

from pyfcm import FCMNotification

API_KEY="[API KEY]"
push_service = FCMNotification(API_KEY)

class SetFCMToken(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		fcmtoken=str(request.json["fcmtoken"])
		if checkToken(ID, token) == -1:
			print('failed to set FCMToken...')
			result={"result":"failed"}
		else:
			sql="UPDATE firebasetoken SET token='"+fcmtoken+"' WHERE id='"+ID+"';"
			manageDB.cur.execute(sql)
			manageDB.conn.commit()
			result={"result":"success"}
		return make_response(jsonify(result), 200)


def sendMessage(TOKEN, body, title, category):
	data_message={
		"body":body,
		"title":title,
		"category":category
	}
	result=push_service.single_device_data_message(registration_id=TOKEN, data_message=data_message)



def noticeOverdue_admin(TOKEN, lockername):
	sendMessage(TOKEN,"물품을 회수할  연체 사물함이 발생했습니다.", lockername, "admin_overdue")

def noticeOverdue_client(TOKEN, lockername):
	sendMessage(TOKEN, "이용중인 사물함의 이용기간이 초과되었습니다. 관리자에게 문의하세요.", "사물함 연체 알림", "client_overdue")

def noticeNotice(title, body):
	sql="SELECT token FROM firebasetoken;"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	length=len(row)
	for i in range(length):
		token=str(row[i][0])
		sendMessage(token, body, title, "notice")

def notice_Illegal_Open(lockername, lockernum):
	sql="SELECT id FROM admin WHERE lockername='"+lockername+"';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	length=len(row)
	now=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	for i in range(length):
		sql="SELECT token FROM firebasetoken WHERE id='"+str(row[i][0])+"';"
		manageDB.cur.execute(sql)
		fetchobject=manageDB.cur.fetchone()
		if fetchobject != None:
			token=str(fetchobject[0])
			sendMessage(token, "사물함 강제 개방이 감지되었습니다.\n 사물함:"+lockername+" 번호:"+str(lockernum), "도난 경보", "illegal_open")
