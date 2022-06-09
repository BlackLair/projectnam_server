import smtplib
from email.mime.text import MIMEText


def sendEmail(receiver, title, body):
    s=smtplib.SMTP('smtp.gmail.com', 587)

    s.starttls()

    s.login('[GMAIL 계정]', '[GMAIL IMAP 암호]')

    msg=MIMEText(body)
    msg['Subject']=title
    msg['To']=receiver
    msg['From']="projectnam.service"
    s.sendmail("projectnam.service", receiver, msg.as_string())
    s.quit()


def EmailVerifying(receiver, name, code):
	title="[프작남]본인 확인용 이메일입니다."
	body="프작남 스마트 사물함을 이용해주셔서 감사합니다.\n\n"+name+" 님의 본인인증을 위한 코드는 다음과 같습니다. : "+code+"\n\n\n 만약 본인이 요청하신 활동이 아니라면 본 이메일로 회신하여 주시기 바랍니다. 감사합니다.\n\n\n"
	sendEmail(receiver, title, body)

def EmailNewAccount(receiver, name):
	title="[프작남]회원가입이 완료되었습니다."
	body=name+" 님, 회원가입이 완료된 것을 축하드립니다. 앞으로도 좋은 서비스를 이용하실 수 있도록 최선을 다하겠습니다.\n이메일 정보는 계정 정보 변경, OTP Key 재발급 등에 활용되며 궁금하신 사항이 있으시다면 projectnam.service.locker@gmail.com으로 문의해주시기 바랍니다. 감사합니다.\n\n"
	sendEmail(receiver, title, body)

def EmailNewAdmin(receiver, lockername, lockercode):
	title="[프작남]관리자 계정이 생성되었습니다."
	body=receiver+" 님의 이메일을 통해 사물함 관리자 계정이 생성되었습니다. 담당 사물함의 이름과 사물함 코드는 다음과 같습니다."+"\n\n\n===========================================\n"+"사물함 이름 : "+lockername+" / 사물함 코드 : "+lockercode+"\n===========================================\n"
	sendEmail(receiver, title, body)

def EmailDeleteAccount(receiver):
	title="[프작남]회원탈퇴가 완료되었습니다."
	body="지금까지 프작남 사물함을 이용해주셔서 감사합니다.\n\n"
	sendEmail(receiver, title, body)


def EmailChangedPassword(receiver, name):
	title="[프작남]비밀번호 변경이 완료되었습니다."
	body=name+" 님의 비밀번호가 변경되었습니다. 이제 새로운 비밀번호로 로그인하실 수 있습니다. 감사합니다.\n\n"
	sendEmail(receiver, title, body)





