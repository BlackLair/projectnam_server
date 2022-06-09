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


서버 측 DB 구조
database:projectnam
	table:admin	// 관리자의 계정 정보 저장 테이블
		col:id		type:VARCHAR length:16 PRIMARY KEY	//관리자의 아이디
		col:pw		type:MEDIUMTEXT		//관리자의 패스워드 password 함수로 암호화
		col:email		type:VARCHAR length:32	//관리자의 이메일 주소
		col:otpkey	type:MEDIUMTEXT		//관리자의 OTP Key  32진수 SHA-1 암호화 키
		col:token		type:MEDIUMTEXT		//관리자 앱 로그인 세션 인증 토큰
		col:status		type:VARCHAR length:10	//관리자 계정 상태
		col:verifyingcode	type:TEXT		//관리자 앱 이메일 인증 코드 및 인증상태
		col:expiretime	type:TEXT		//관리자 앱 이메일 인증 코드 만료시간
		lockername	type:VARCHAR length:32	//관리자 담당 사물함 이름
	table:client	// 사용자의 계정 정보 저장 테이블
		col:name		type:MEDIUMTEXT		//사용자의 이름
		col:email		type:MEDIUMTEXT		//사용자의 이메일 주소
		col:id		type:VARCHAR length:50 PRIMARY KEY	//사용자의 아이디
		col:pw		type:MEDIUMTEXT		//사용자의 패스워드 password 함수로 암호화
		col:status		type:MEDIUMTEXT		//사용자의 예약 상태
		col:otpkey	type:MEDIUMTEXT		//사용자의 OTP Key
		col:token		type:MEDIUMTEXT		//사용자 앱 로그인 세션 인증 토큰
		col:verifyingcode	type:TEXT		//사용자 앱 이메일 인증 코드 및 인증상태
		col:expiretime	type:TEXT		//사용자 앱 이메일 인증 코드 만료시간
		col:startdate	type:DATE		//사물함 대여 시작 날짜
		col:enddate	type:DATE		//사물함 대여 종료 날짜
		col:usinglockername type:TEXT		//사용중인 사물함 이름
	table:firebasetoken	//푸시 알림을 보내기 위한 계정별 firebase token 저장 테이블
		col:id		type:VARCHAR length:20 PRIMARY KEY	//계정 아이디
		col:token		type:TEXT		//firebase token
	table:lockers	//각 사물함의 정보 저장 테이블
		col:lockername	type:MEDIUMTEXT		//사물함 이름
		col:location	type:MEDIUMTEXT		//사물함이 위치한 주소
		col:ip		type:MEDIUMTEXT		//사물함이 접속된 IP 주소
		col:otpKey	type:MEDIUMTEXT		//사물함 자체 인증용 OTP Key
		col:maxspaces	type:INT length:11		//사물함 최대 보관함 개수
		col:usedspaces	type:INT length:11		//현재 사용 중인 보관함+현재 예약 상태 개수
		col:signedID	type:TEXT		//사물함에 현재 로그인 중인 계정 아이디
		col:status		type:TEXT		//로그인 인증 상황
		col:lockercode	type:VARCHAR length:64 PRIMARY KEY	//관리의 사물함 등록 위한 고유 코드
	table:[사물함 이름]	//해당 사물함의 예약 현황을 저장할 테이블. 새로운 사물함이 등록될 때마다 사물함 이름으로 생성됨
		col:num		type:INT length:11 PRIMARY KEY		//예약 고유번호
		col:status		type:INT length:11		//연체 상태
		col:clientid	type:TEXT		//예약자 아이디
		col:reserveddate	type:DATE		//예약 날짜
		col:lockernum	type:INT			//할당된 사물함 번호
	table:notice	//공지사항 저장 테이블
		col:num		type:INT length:11 PRIMARY KEY		//공지사항 고유 번호
		col:title		type:MEDIUMTEXT		//공지사항 제목
		col:date		type:MEDIUMTEXT		//공지사항 작성시간
		col:body		type:MEDIUMTEXT		//공지사항 내용
	table:illegal_open_log	//사물함의 도난 경보 이력 저장 테이블
		col:num		type:INT length:11 PRIMARY KEY		//도난 이력 고유 번호
		col:lockername	type:VARCHAR length:32	//도난이 발생한 사물함 이름
		col:lockernum	type:INT length:11		//도난이 발생한 사물함 번호
		col:time		type:DATETIME		//도난이 발생한 시간
	table:overdue_log		//연체 사물함 이력 저장 테이블
		col:num		type:INT length:11 PRIMARY KEY		//연체 발생 고유 번호
		col:name		type:VARCHAR length:16	//연체 사용자 이름
		col:id		type:VARCHAR length:16	//연체 사용자 아이디
		col:email		type:TINYTEXT		//연체 사용자 이메일
		col:lockername	type:TEXT		//연체된 사물함 이름
		col:lockernum	type:INT length:11		//연체된 사물함 번호
		col:startdate	type:DATE		//예약했던 사용 시작 날짜
		col:enddate	typeDATE		//예약했던 사용 종료 날짜
		col:iscollected	type:VARCHAR length:5	//관리자의 물품 회수 여부
		col:returntime	type:DATETIME		//사용자에게 물품 반환 여부. NULL일 경우 미반환
