from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, reqparse
from checkLoginToken import *
import json, datetime
import time
import manageDB, manageFCM

def getNoticeCount():
    sql="SELECT COUNT(*) FROM notice;"
    manageDB.cur.execute(sql)    # 공지사항 갯수 가져오기
    maxIndex=int(manageDB.cur.fetchone()[0])
    return maxIndex


class LoadNotice(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        if checkToken(ID, token) == -1:
            print('token not match...')
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        maxIndex=getNoticeCount()
        diff=(int(request.json["page"]))*10
        offset=maxIndex-diff
        if offset<0:
            offset=0
        sql="SELECT * FROM notice limit 10 offset "+str(offset)+";"
        manageDB.cur.execute(sql)    # 공지사항 내용 가져오기
        result = json.dumps(manageDB.cur.fetchall())
        return make_response(result, 200)

class LoadNoticeCount(Resource):
    def get(self):
        maxIndex=getNoticeCount()
        result={"maxindex":maxIndex}
        return make_response(jsonify(result), 200);


class UploadNotice(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        title=str(request.json["title"])
        body=str(request.json["body"])
        pushtoclient=str(request.json["pushtoclient"])
        currtime=datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        if checkToken_only_admin(ID, token) == -1:
            print('token not match...')
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        sql="INSERT INTO notice(title, date, body) VALUE('"+title+"', '"+currtime+"', '"+body+"');"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success"}
        time.sleep(1.5)
        if pushtoclient=="true":
            manageFCM.noticeNotice(title, body)
        return make_response(jsonify(result), 200)

class DeleteNotice(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        num=int(request.json["num"])
        if checkToken_only_admin(ID, token) == -1:
            print('token not match...')
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        sql="DELETE FROM notice WHERE num = "+str(num)+" ;"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        print("Notice deleted.(index:"+str(num)+")")
        result={"result":"success"}
        time.sleep(1)
        return make_response(jsonify(result), 200)
