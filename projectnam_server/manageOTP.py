import pyotp
import hashlib
import hmac
import base64
import datetime
import manageDB

def instance_otp():
	#즉석 otp
	totp=pyotp.TOTP(pyotp.random_base32())
	return totp.now()


def check_otp_for_locker(lockername, locker_otp, receivedtimestr):
	sql="SELECT otpKey FROM lockers WHERE lockername='"+lockername+"';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	if row == None:
		return -1
	key=str(row[0][0])
	totp=pyotp.TOTP(base64.b32encode(bytes(key, 'utf-8')), 6, hashlib.sha256)
	receivedtime=datetime.datetime.strptime(receivedtimestr, '%Y-%m-%d %H:%M:%S.%f')
	currtime=datetime.datetime.now()
	if currtime>=receivedtime :
		diff=(currtime-receivedtime).seconds.numerator
	else :
		diff=(receivedtime-currtime).seconds.numerator
	server_otp=totp.at(receivedtime)
	print(server_otp)
	if diff >= 20 or diff <= -20 :   # 수신받은 시간초가 현재와 20초 이상 차이날 경우
		return -2
	print(server_otp)
	if server_otp==locker_otp :
		return 1
	else:
		return 0

def check_otp_for_client(ID, client_otp):
	sql="SELECT otpkey FROM client WHERE id='"+ID+"';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchall()
	key=str(row[0][0])
	currtime=str(datetime.datetime.now())
	totp=pyotp.TOTP(base64.b32encode(bytes(key, 'utf-8')),6,hashlib.sha256)
	server_otp=totp.at(datetime.datetime.strptime(currtime, '%Y-%m-%d %H:%M:%S.%f'))
	if server_otp==client_otp:
        	return 1
	else:
		return 0

def check_otp_for_admin(ID, admin_otp):
	sql="SELECT otpkey FROM admin WHERE id='"+ID+"';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchone()
	key=str(row[0])
	currtime=str(datetime.datetime.now())
	totp=pyotp.TOTP(base64.b32encode(bytes(key, 'utf-8')),6,hashlib.sha256)
	server_otp=totp.at(datetime.datetime.strptime(currtime, '%Y-%m-%d %H:%M:%S.%f'))
	if server_otp==admin_otp:
		return 1
	else:
		return 0

def generate_otp_key():
	otpkeyb32=pyotp.random_base32()
	key=base64.b32encode(bytearray(otpkeyb32, 'ascii')).decode('utf-8')
	return key
