import time, datetime

from flask import Flask, jsonify, request, make_response
from flask_restful import Resource

import manageDB, manageOTP
import manageEmail

class NewAccountApi(Resource):
    def post(self):
        print(request.get_json())
        name=str(request.json["name"])
        email=str(request.json["email"])
        ID=str(request.json["newId"])
        PW=str(request.json["pw"])
        print(name)

        #중복 아이디 존재 확인, 중복 시 409 리턴
        sql="SELECT id FROM client WHERE id='"+ID+"';"
        sql2="SELECT id FROM admin WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        manageDB.cur.execute(sql2)
        row2=manageDB.cur.fetchone()
        if row != None or row2 != None: # 중복 아이디일 경우
            print('duplicated id...')
            result={"result":"duplicated"}
            return make_response(jsonify(result), 200)
        key=manageOTP.generate_otp_key()
        sql="INSERT INTO client VALUES('"+name+"','"+email+"','"+ID+"',password('"+PW+"'),'idle','"+key+"','0', '0', '0', NULL, NULL, '0');"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        sql="INSERT INTO firebasetoken VALUES('"+ID+"', '0');"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"otpkey":key , "result":"success"}
        manageEmail.EmailNewAccount(email, name)
        return make_response(jsonify(result), 200)

class Login_client(Resource):
    def post(self):
        print(request.get_json())
        ID=str(request.json["id"])
        PW=str(request.json["pw"])
        token=manageOTP.generate_otp_key()
        sql="SELECT id, name , email FROM client WHERE id='"+ID+"' AND pw=password('"+PW+"');"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if row == None : #해당되는 회원정보가 없을 경우
            result={"result":"no match"}
            return make_response(jsonify(result), 200)
        name=str(row[1])
        email=str(row[2])
        sql="UPDATE client SET token='"+token+"' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success", "name":name, "email":email, "token":token}
        return make_response(jsonify(result), 200)

class Logout_client(Resource):
    def post(self):
        ID=str(request.json["id"])
        IP=request.remote_addr
        token=str(request.json["token"])
        sql="UPDATE client SET token = '0', verifyingcode='0' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result = {"result":"success"}
        return make_response(jsonify(result), 200)





class Send_Verifying_Email(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        sql="SELECT id, email, name, token FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchall()
        if row == None:
            result={"result":"no match"}
            return make_response(jsonify(result), 200)
        if row[0][3] != token:
            result={'result':'diffIP'}
            return make_response(jsonify(result), 200)
        code=str(manageOTP.instance_otp())
        email=row[0][1]
        name=row[0][2]
        expiretime=str(datetime.datetime.now()+datetime.timedelta(minutes=2))
        sql="UPDATE client SET verifyingcode ='"+code+"', expiretime ='"+expiretime+"' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        manageEmail.EmailVerifying(email, name, code)
        result = {"result":"success"}
        return make_response(jsonify(result), 200)

class Verifying_Code(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        code=str(request.json["code"])
        sql="SELECT id, token, verifyingcode, expiretime FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchall()
        if row[0][1] != token:
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        expiretime=datetime.datetime.strptime(row[0][3], '%Y-%m-%d %H:%M:%S.%f')
        if expiretime < datetime.datetime.now():
            result={"result":"expired"}
            return make_response(jsonify(result), 200)
        if row[0][2] != code:
            result={"result":"not match"}
            return make_response(jsonify(result), 200)
        sql="UPDATE client SET expiretime = '1970-01-01 23:59:59.000001' , verifyingcode = 'verified' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success"}
        return make_response(jsonify(result), 200)

class Unverifying_Code(Resource):
    def post(self):
        ID=str(request.json["id"])
        sql="SELECT id FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchall()
        if row == None:
            result={"result":"failed"}
            return make_response(jsonify(result), 200)
        sql="UPDATE client SET verifyingcode = '0', expiretime = '1970-01-01 23:59:59.000001' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success"}
        return make_response(jsonify(result), 200)

class Change_Password(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        newPW=str(request.json["newpw"])
        oldPW=str(request.json["oldpw"])
        sql="SELECT token, verifyingcode FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if str(row[0]) != token:
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        if str(row[1]) != "verified":
            print('not verified...')
            result={"result":"not verified"}
            return make_response(jsonify(result), 200)
        sql="SELECT id FROM client WHERE id='"+ID+"' AND pw=password('"+oldPW+"');"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if row == None:
            print('old password not correct...')
            result={"result":"old pw incorrect"}
            return make_response(jsonify(result), 200)
        sql="UPDATE client SET pw=password('"+newPW+"') WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success"}
        return make_response(jsonify(result), 200)

class Reissuance_OTPKey(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        sql="SELECT token, verifyingcode FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if str(row[0]) != token:
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        if str(row[1]) != "verified":
            result={"result":"not verified"}
            return make_response(jsonify(result), 200)
        newKey=manageOTP.generate_otp_key()
        sql="UPDATE client SET otpkey='"+newKey+"' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success", "otpkey":newKey}
        return make_response(jsonify(result), 200)

class Delete_account(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        sql="SELECT token, verifyingcode, status FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if str(row[0]) != token:
            print('diffIP')
            result={"result":"diffIP"}
            return make_reponse(jsonify(result), 200)
        if str(row[1]) != "verified":
            print('not verified...')
            result={"result":"not verified"}
            return make_response(jsonify(result), 200)
        if str(row[2]) != "idle":
            print('Status is not idle...')
            result={"result":"not idle"}
            return make_response(jsonify(result), 200)
        sql="DELETE FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        sql="DELETE FROM firebasetoken WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        sql="SELECT COUNT(id) FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if row[0] == 0 :
            result={"result":"success"}
        else :
            result={"result":"failed"}
        return make_response(jsonify(result), 200)
