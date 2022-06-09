import manageDB


def checkToken(ID, inputToken):
	sql="SELECT token FROM client WHERE id='"+ID+"';"
	manageDB.cur.execute(sql)
	row=manageDB.cur.fetchone()
	if row == None:
		sql="SELECT token FROM admin WHERE id='"+ID+"';"
		sql=manageDB.cur.execute(sql)
		row=manageDB.cur.fetchone()
		if row == None:
			return -1
	token=row[0]
	if inputToken == token:
		return 0
	else:
		return -1

def checkToken_only_admin(ID, inputToken):
	sql="SELECT token FROM admin WHERE id='"+ID+"';"
	sql=manageDB.cur.execute(sql)
	row=manageDB.cur.fetchone()
	if row == None:
		return -1
	token=row[0]
	if inputToken==token:
		return 0
	else:
		return -1
