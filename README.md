# projectnam_server
2022년 성결대학교 졸업작품 - 서버 측 소스코드

AWS EC2 Cloud Compute - free tier
Amazon Linux 2 AMI
Python 3.7

pip dependencies ( 설치방법 : #pip install flask )
flask
flask_restful
schedule
pyotp
pyfcm
smtplib
mariadb

main execution file : projectNam.py

실행 명령어
$python3 projectNam.py

백그라운드 실행 명령어 : SSH 원격 접속이 종료되어도 프로그램이 계속 실행되며, nohup.out이라는 파일에 로그가 저장된다.
$nohup python3 projectNam.py

유의사항
Firebase Cloud Messaging Service API Key : manageFCM.py에 하드코딩
google Email 계정 정보 : manageEmail.py에 하드코딩
Datebase 계정 : manageDB.py에 하드코딩
API 추가 시 : projectNam.py에 추가. 새 .py파일일 경우 from [파일명.py] import * 추가
