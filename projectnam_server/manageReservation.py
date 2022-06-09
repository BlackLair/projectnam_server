import time, datetime

from flask import Flask, jsonify, request, make_response
from flask_restful import Resource
import json
import manageDB
import manageEmail


class CheckReservationStatus(Resource):
    def post(self):
        result={"result":"empty"}
        ID=str(request.json["id"])
        token=str(request.json["token"])
        sql="SELECT id, token, status, startdate, enddate, usinglockername FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if str(row[1]) != token:
            print("token not match")
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        if str(row[2]) == "idle":
            print('client is idle.')
            result={"result":"idle"}
            return make_response(jsonify(result), 200)
        elif str(row[2]) == "reserved" or str(row[2])=="using" or str(row[2])=="overdue":
            sql="SELECT location FROM lockers WHERE lockername='"+row[5]+"';"
            manageDB.cur.execute(sql)
            row2=manageDB.cur.fetchone()
            result={"result":"reserved", "startdate":str(row[3]), "enddate":str(row[4]), "usinglockername":str(row[5]), "location":str(row2[0])}
            if str(row[2])=="using" or str(row[2])=="overdue":
                if str(row[2])=="using":
                    print('client is using.')
                    result['result']="using"
                else:
                    print('client overdue...')
                    result['result']="overdue"
                sql="SELECT lockernum FROM "+str(row[5])+" WHERE clientid='"+str(row[0])+"';"
                manageDB.cur.execute(sql)
                row3=manageDB.cur.fetchone()
                result['lockernum']=int(row3[0])
            elif str(row[2])=="reserved":
                print('client is already reserved.')
        return make_response(jsonify(result), 200)

class LoadLockerCount(Resource):
    def get(self):
        sql="SELECT COUNT(*) FROM lockers"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        count=int(row[0])
        result={"result":count}
        return make_response(result, 200)

class LoadLockerNames(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        result=manageDB.getDB("client", "token")
        if result==None:
            print("token not match")
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        sql="SELECT lockername, location FROM lockers"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchall()
        result = json.dumps(row)
        return make_response(result, 200)


class LoadFullReservedDate(Resource):
    def post(self):
        lockername=str(request.json["lockername"])
        sql="SELECT maxspaces FROM lockers WHERE lockername='"+lockername+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if row[0] == None:
            print('lockername '"+lockername+"' doesn\'t exist...')
            result={"result":"no locker"}
            return make_response(jsonify(result), 200)
        print(lockername+" maxspaces : "+str(row[0]))
        sql="SELECT CAST(reserveddate AS CHAR) FROM "+lockername+" GROUP BY reserveddate HAVING COUNT(reserveddate) = "+str(row[0])+";"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchall()
        result=json.dumps(row)
        return make_response(result, 200)

class Cancel_Reservation(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        sql="SELECT status, token, startdate, usinglockername FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        lockername=str(row[3])
        if row[1] != token:
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        elif row[0] != "reserved":
            print('Client isn\'t reserved...')
            result={"result":"not reserved"}
            return make_response(jsonify(result), 200)
        startdate=datetime.datetime.strptime(str(row[2]), '%Y-%m-%d')
        today=datetime.datetime.now()
        if today >= startdate:
            sql="SELECT usedspaces FROM lockers WHERE lockername='"+lockername+"';"
            manageDB.cur.execute(sql)
            row=manageDB.cur.fetchone()
            usedspaces=int(row[0])
            sql="UPDATE lockers SET usedspaces="+str(usedspaces)+" WHERE lockername='"+lockername+"';"
            manageDB.cur.execute(sql)
            manageDB.conn.commit()
        sql="UPDATE client SET status='idle', startdate=NULL, enddate=NULL, usinglockername=NULL WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        sql="DELETE FROM "+lockername+" WHERE clientid='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        result={"result":"success"}
        return make_response(jsonify(result), 200)

class Reservation(Resource):
    def post(self):
        ID=str(request.json["id"])
        token=str(request.json["token"])
        lockername=str(request.json["lockername"])
        #reservetype=str(request.json["reservetype"])
        startdate=str(request.json["startdate"])
        enddate=str(request.json["enddate"])
        print(lockername+", "+startdate+" ~ "+enddate)
        sql="SELECT status, token FROM client WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        clientinfo=manageDB.cur.fetchone()
        if clientinfo[1] != token:
            result={"result":"diffIP"}
            return make_response(jsonify(result), 200)
        elif clientinfo[0] != "idle":
            print('client is not idle...')
            result={"result":"not idle"}
            if clientinfo[0]=="overdue":
                result['result']="overdue"
            return make_response(jsonify(result), 200)
        sql="SELECT maxspaces FROM lockers WHERE lockername='"+lockername+"';"
        manageDB.cur.execute(sql)
        maxspaces=str(manageDB.cur.fetchone()[0])
        sql="SELECT CAST(reserveddate AS CHAR) FROM "+lockername+" WHERE reserveddate BETWEEN date('"+startdate+"') AND date('"+enddate+"') GROUP BY reserveddate HAVING COUNT(reserveddate)="+maxspaces+";"
        manageDB.cur.execute(sql)
        row=manageDB.cur.fetchone()
        if row != None :
            print('could not reservate... : full reservation')
            result={"result":"full"}
            return make_response(jsonify(result), 200)
        t_tempdate=datetime.datetime.strptime(startdate, '%Y-%m-%d')
        t_enddate=datetime.datetime.strptime(enddate, '%Y-%m-%d')+datetime.timedelta(days=1)
        while t_tempdate != t_enddate:
            sql="INSERT INTO "+lockername+"(status, clientid, reserveddate) VALUES(0, '"+ID+"','"+t_tempdate.strftime("%Y-%m-%d")+"');"
            manageDB.cur.execute(sql)
            manageDB.conn.commit()
            t_tempdate+=datetime.timedelta(days=1)
        print('reservation list updated.')
        sql="UPDATE client SET status='reserved', startdate='"+startdate+"', enddate='"+enddate+"', usinglockername='"+lockername+"' WHERE id='"+ID+"';"
        manageDB.cur.execute(sql)
        manageDB.conn.commit()
        print('client reservation status updated.')
        result={"result":"success"}
        return make_response(jsonify(result), 200)
