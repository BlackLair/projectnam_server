import time, datetime

from flask import Flask, jsonify, request, make_response
from flask_restful import Resource

import manageDB, manageOTP
import manageEmail
from checkLoginToken import *

class NewAdmin_Account(Resource):
	def post(self):
		ID=str(request.json["newid"])
		PW=str(request.json["pw"])
		email=str(request.json["email"])
		lockercode=str(request.json["lockercode"])
		print('id:'+ID+' email:'+email+' lockercode:'+lockercode)
		sql="SELECT id FROM client WHERE id='"+ID+"';"
		sql2="SELECT id FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		manageDB.cur.execute(sql2)
		row2=manageDB.cur.fetchone()
		if row != None or row2 != None:
			print('duplicated id...')
			result={"result":"duplicated"}
			return make_response(jsonify(result), 200)
		sql="SELECT lockername FROM lockers WHERE lockercode='"+lockercode+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			print('lockercode doesn\'t exist.')
			result={"result":"no lockercode"}
			return make_response(jsonify(result), 200)
		key=manageOTP.generate_otp_key()
		lockername=str(row[0])
		sql="INSERT INTO admin(id, token, pw, email, otpkey, status, lockername) VALUES('"+ID+"', '0', password('"+PW+"'), '"+email+"', '"+key+"', 'idle', '"+lockername+"')"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		sql="INSERT INTO firebasetoken(id, token) VALUES('"+ID+"', '0');"
		result={"otpkey":key, "lockername":lockername, "result":"success"}
		manageEmail.EmailNewAdmin(email, lockername, lockercode)
		return make_response(jsonify(result), 200)


class Admin_login(Resource):
	def post(self):
		ID=str(request.json["id"])
		PW=str(request.json["pw"])
		token=manageOTP.generate_otp_key()
		sql="SELECT email, lockername FROM admin WHERE id='"+ID+"' AND pw=password('"+PW+"');"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			print('admin login failed...:no match')
			result={"result":"no match"}
			return make_response(jsonify(result), 200)
		email=str(row[0])
		lockername=str(row[1])
		sql="SELECT location FROM lockers WHERE lockername='"+lockername+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		location=str(row[0])
		sql="UPDATE admin SET token='"+token+"' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success", "email":email, "lockername":lockername, "token":token, "location":location}
		return make_response(jsonify(result), 200)

class Admin_logout(Resource):
	def post(self):
		ID=str(request.json["id"])
		sql="UPDATE admin SET token='0', verifyingcode='0', expiretime='1970-01-01 23:59:59.000001' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)

class Send_Verifying_Email_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT email from admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		email=str(row[0])
		expiretime=str(datetime.datetime.now()+datetime.timedelta(minutes=2))
		code=str(manageOTP.instance_otp())
		sql="UPDATE admin SET verifyingcode='"+code+"', expiretime='"+expiretime+"' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		manageEmail.EmailVerifying(email, ID, code)
		result = {"result":"success"}
		return make_response(jsonify(result), 200)

class Verifying_Code_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		code=str(request.json["code"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT verifyingcode, expiretime FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		correctcode=str(row[0])
		expiretime=datetime.datetime.strptime(row[1], '%Y-%m-%d %H:%M:%S.%f')
		if expiretime < datetime.datetime.now():
			result={"result":"expired"}
			print('code expired...')
			return make_response(jsonify(result), 200)
		if correctcode!=code:
			print('code not match...')
			result={"result":"not match"}
			return make_response(jsonify(result), 200)
		sql="UPDATE admin SET expiretime = '1970-01-01 23:59:59.000001', verifyingcode = 'verified' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)

class Unverifying_Code_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		sql="SELECT id FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			print("not exist...")
			result={"result":"failed"}
			return make_response(jsonify(result), 200)
		sql="UPDATE admin SET verifyingcode = '0', expiretime='1970-01-01 23:59:59.000001' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)

class Change_Password_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		newPW=str(request.json["newpw"])
		oldPW=str(request.json["oldpw"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT verifyingcode FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		isVerified=str(row[0])
		if isVerified != 'verified':
			print('not verified...')
			result={"not verified"}
			return make_response(jsonify(result), 200)
		sql="SELECT id FROM admin WHERE id='"+ID+"' AND pw=password('"+oldPW+"');"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			print('old password not correct...')
			result={"result":"old pw incorrect"}
			return make_response(jsonify(result), 200)
		sql="UPDATE admin SET pw=password('"+newPW+"') WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)

class Reissuance_OTPKey_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT verifyingcode FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		isVerified=str(row[0])
		if isVerified != "verified":
			result={"result":"not verified"}
			print("not verified...")
			return make_response(jsonify(result), 200)
		newKey=manageOTP.generate_otp_key()
		sql="UPDATE admin SET otpkey='"+newKey+"' WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success" ,"otpkey":newKey}
		return make_response(jsonify(result), 200)

class Delete_Account_Admin(Resource):
	def post(self):
		ID=str(request.json["id"])
		token=str(request.json["token"])
		if checkToken_only_admin(ID, token) == -1:
			print('token not match...')
			result={"result":"diffIP"}
			return make_response(jsonify(result), 200)
		sql="SELECT verifyingcode FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		isVerified=str(row[0])
		if isVerified != "verified":
			result={"result":"not verified"}
			print('not verified...')
			return make_response(jsonify(result), 200)
		sql="DELETE FROM admin WHERE id='"+ID+"';"
		manageDB.cur.execute(sql)
		manageDB.conn.commit()
		result={"result":"success"}
		return make_response(jsonify(result), 200)

