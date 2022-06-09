from manageAccount import *
from manageNotice import *
from InitLocker import *
from manageLockerService import *
from manageReservation import *
from manageAdminAccount import *
from manageLockerAdmin import *
from manageFCM import *


from flask import jsonify
from flask import request, Flask, make_response
from flask_restful import Resource, Api

import manageOverdue

app = Flask(__name__)
api = Api(app)
print('initiate2')
api.add_resource(NewAccountApi, '/newaccount')
api.add_resource(Login_client, '/client/login')
api.add_resource(Logout_client, '/client/logout')

api.add_resource(Send_Verifying_Email, '/client/send_verifying_email')
api.add_resource(Verifying_Code, '/client/verifying_code')
api.add_resource(Unverifying_Code, '/client/unverifying_code')
api.add_resource(Change_Password, '/client/change_password')
api.add_resource(Reissuance_OTPKey, '/client/reissuance_otpkey')
api.add_resource(Delete_account, '/client/delete_account')

api.add_resource(CheckReservationStatus, '/client/reservation/check_reservation_status')
api.add_resource(LoadLockerCount, '/client/reservation/load_locker_count')
api.add_resource(LoadLockerNames, '/client/reservation/load_locker_names')
api.add_resource(LoadFullReservedDate, '/client/reservation/load_full_reserved_dates')
api.add_resource(Reservation, '/client/reservation/reserve')
api.add_resource(Cancel_Reservation, '/client/reservation/cancel')

api.add_resource(LoadNotice, '/notice/load')
api.add_resource(LoadNoticeCount, '/notice/loadcount')
api.add_resource(UploadNotice, '/notice/upload')
api.add_resource(DeleteNotice, '/notice/delete')

api.add_resource(Connect_Locker, '/locker/connect')
api.add_resource(Login_Locker, '/locker/login')
api.add_resource(Login_Locker_OTP, '/locker/verify_OTP')
api.add_resource(Activate_Locker, '/locker/activate')
api.add_resource(Deactivate_Locker, '/locker/deactivate')
api.add_resource(Oneday_Rent, '/locker/oneday_rent')
api.add_resource(Illegal_Open_Detected, '/locker/illegal_open_detected')

api.add_resource(NewAdmin_Account, '/admin/new_account')
api.add_resource(Admin_login, '/admin/login')
api.add_resource(Admin_logout, '/admin/logout')
api.add_resource(Send_Verifying_Email_Admin, '/admin/send_verifying_email')
api.add_resource(Verifying_Code_Admin, '/admin/verifying_code')
api.add_resource(Unverifying_Code_Admin, '/admin/unverifying_code')
api.add_resource(Change_Password_Admin, '/admin/change_password')
api.add_resource(Reissuance_OTPKey_Admin, '/admin/reissuance_otpkey')
api.add_resource(Delete_Account_Admin, '/admin/delete_account')


api.add_resource(Load_locker_status, '/admin/manage/load_locker_status')
api.add_resource(Load_locker_details, '/admin/manage/load_locker_details')
api.add_resource(Load_Illegal_Open_History, '/admin/manage/load_illegal_open_history')

api.add_resource(manageOverdue.Load_Overdue_List, '/admin/load_overdue_list')
api.add_resource(manageOverdue.Collect_Overdue_Storage, '/admin/collect_overdue_storage')
api.add_resource(manageOverdue.Return_Overdue_Storage, '/admin/return_overdue_storage')

api.add_resource(SetFCMToken, '/setfcmtoken')


if __name__== '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
# test
