import sys
import mariadb

from flask import json
try:
    conn = mariadb.connect(user="[DB계정이름]", password="[DB계정암호]", host="127.0.0.1", port=3306, database="projectnam")
except mariadb.Error as e:
        print(f"Error Connecting to MariaDB Platform: {e}")
        sys.exit(1)
cur = conn.cursor()
sql="set global interactive_timeout=31536000"
sql2="set global wait_timeout=31536000"
cur.execute(sql)
cur.execute(sql2)
sql="set session interactive_timeout=31536000"
sql2="set session wait_timeout=31536000"
cur.execute(sql)
cur.execute(sql2)

def getDB(TABLE, KEY):
	sql="SELECT "+KEY+" FROM "+TABLE+";"
	cur.execute(sql)
	row=cur.fetchone()
	if row==None:
		return None
	else:
		return row[0][0]
def setDBString(TABLE, WHEREKEY, WHEREVALUE, KEY, VALUE):
	sql="UPDATE "+TABLE+" SET "+KEY+"='"+VALUE+"' WHERE "+WHEREKEY+"='"+WHEREVALUE+"';"
	cur.execute(sql)
	conn.commit()

def setDBInt(TABLE, WHEREKEY, WHEREVALUE, KEY, VALUE):
	sql="UPDATE "+TABLE+" SET "+KEY+"="+VALUE+" WHERE "+WHEREKEY+"='"+WHEREVALUE+"';"
	cur.execute(sql)
	conn.commit()
