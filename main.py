import psycopg2
import sys
from datetime import datetime,UTC

# fetch the config
db = #something from config
user = #something from config
ps = #something from config

conn = psycopg2.connect("dbname=%s user=%s password=%s" % (db,user,ps))

def doy2monthdate(year,day):
	date_string = "%s %s" % (year,day)
	date_object = datetime.strptime(date_string, '%Y %j')
	return date_object.strftime('%b%d').upper()

def timestmp():
	now = datetime.now(UTC)
	formatted_time = now.strftime("%j/%H%M")
	return formatted_time.upper()

def pad(num,spaces):
	tnum = num
	while len(tnum)<spaces:
		tnum = "0" + tnum
	return tnum

def findcars(legid,accomtype,curs):
	if accomtype != 'A':
		findcarsq = "SELECT capacity, carid, id, trainid FROM cardatetrain WHERE legid=%s AND accomtype='%s';" % (legid, accomtype)
	else:
		findcarsq = "SELECT capacity, carid, id, trainid FROM cardatetrain WHERE legid=%s;" % (legid)
	curs.execute(findcarsq)
	foundcars = curs.fetchall()
	return foundcars

def fetchcar(legid,carcode,accomtype,curs,remcap=True):
	foundcars = findcars(legid,accomtype,curs)
	matchedcar = ''
	if carcode not in ["00"]: # not a control code, ergo they want a specific car
		outlst = []
		for car in foundcars:
			cardateid = car[2]
			finduseq = "SELECT reservedseats FROM cardateusage WHERE cardateid=%s;" % cardateid
			curs.execute(finduseq)
			try:
				usedseats = curs.fetchone()[0]
			except TypeError:
				usedseats = 0
			if remcap: # remaining capacity, probably all we care about
				usage = car[0] - usedseats
			else:
				usage = car[0] # technically not usage, but w/e
			if carcode == '99':
				outlst.append((usage,car[1],car[2],legid))
			elif car[1].endswith(carcode):
				outlst.append((usage,car[1],car[2],legid))
		return outlst
	else:
		raise NotImplementedError


def queryleg(legid, carcode,accomtype, curs):
	fetchedcars = fetchcar(legid,carcode,accomtype,curs,remcap=True)
	return fetchedcars

def findroutelegs(startleg,endleg,curs,westbound=True):
	fetchstartq = "SELECT startindex, date, dayoftrain, trainid FROM legedgeindex WHERE legid=%s;" % startleg
	curs.execute(fetchstartq)
	startindex, date, dayoftrain, trainid = curs.fetchall()[0]
	fetchendq = "SELECT endindex FROM legedgeindex WHERE legid=%s;" % endleg
	curs.execute(fetchendq)
	endindex = curs.fetchone()[0]
	if endindex != startindex:
		if westbound:
			sort = "ASC"
		else:
			sort = "DESC"
		findorderedq = '''SELECT legid 
			FROM legedgeindex 
			WHERE %s <= startindex 
			AND endindex <= %s 
			AND trainid='%s' 
			AND date - dayoftrain = %s
			ORDER BY startindex %s;''' % (startindex,endindex,trainid,date-dayoftrain,sort)
		curs.execute(findorderedq)
		legs = curs.fetchall()
		outlegs = []
		for leg in legs:
			outlegs.append(leg[0])
		return outlegs

def findextremelegs(startcity,endcity,trainid,date,curs):
	findstartlegq = '''SELECT legid, date, startcity, endcity, startindex, dayoftrain 
			FROM legedgeindex 
			WHERE startcity='%s' 
			AND trainid='%s' 
			AND date = %s 
			ORDER BY startindex ASC;''' \
			% (startcity,trainid,date)
	curs.execute(findstartlegq)
	foundlegs = [curs.fetchone()]
	dayoftrain = foundlegs[0][5]
	findendlegq = '''SELECT legid, date, startcity, endcity, startindex 
			FROM legedgeindex 
			WHERE endcity='%s' 
			AND trainid='%s' 
			AND date - dayoftrain + %s = %s 
			ORDER BY startindex ASC;''' \
			% (endcity,trainid,dayoftrain,date)
	curs.execute(findendlegq)
	foundlegs.append(curs.fetchone())
	return foundlegs

def cancelreso(resid,curs):
	dellegresq = "DELETE FROM legreservations WHERE reservationid=%s" % resid
	delresoq = "DELETE FROM reservations WHERE id=%s" % resid
	curs.execute(dellegresq)
	curs.execute(delresoq)
	return 0

def reducereso(resid,seats,curs):
	reduresoq = "UPDATE reservations SET seats=seats-%s WHERE id=%s" % (seats,resid)
	curs.execute(reduresoq)
	return 0

def cancel(carcode,trainid,date,startcity,endcity,reqseats,accomreq,curs,year=1967,westbound=True):
	if carcode in ['00','99']:
		return [2,"INVCAR"] # can't be a control code
	# find a car ID
	extremelegs = findextremelegs(startcity,endcity,trainid,date,curs)
	carid = fetchcar(extremelegs[0][0],carcode,accomreq,curs)[0][1]
	findresosq = '''SELECT id,seats FROM reservations 
			WHERE startcity='%s' AND date='%s' 
			AND car='%s' AND endcity='%s';''' \
			% (startcity,date,carid,endcity)
	curs.execute(findresosq)
	resos = curs.fetchall()
	remainingseats = reqseats
	subresos = []
	for reso in resos:
		if reso[1] == remainingseats: # a reservation with the same # of seats
			subresos = [reso]
			break
		elif reso[1] < remainingseats: # many small reservations equal a big one
			subresos.append(reso)
	while remainingseats > 0 and len(subresos) > 0:
		if subresos[0][1] == remainingseats:
			cancelreso(subresos[0][0],curs)
			remainingseats = 0
		elif subresos[0][1] < remainingseats:
			cancelreso(subresos[0][0],curs)
			remainingseats = remainingseats - subresos[0][1]
			subresos.pop(0)
		else:
			reducereso(subresos[0][0],remainingseats,curs)
			remainingseats = 0
	ts = timestmp()
	dt = doy2monthdate(year,date)
	if remainingseats == 0:
		outstr = "CL%s%s %s %s" % (trainid,carcode,dt, ts)
		return (0,outstr)
	else:
		return [1,"INVQTY"]

def getcaps(startcity,endcity,trainid,date,westbound,carcode,accomreq,curs):
	foundlegs = findextremelegs(startcity,endcity,trainid,date,curs)
	capacity = 0
	mincap = dict()
	cars=[]
	carlegs=dict()
	if len(foundlegs) == 1: #it's a single leg trip
		legid = foundlegs[0][0]
		legs = [legid]
		cars = queryleg(legid,carcode,accomreq,curs)
	else:
		startleg = foundlegs[0][0]
		endleg = foundlegs[1][0]
		legs = findroutelegs(startleg,endleg,curs,westbound)
		for legid in legs:
			car = queryleg(legid,carcode,accomreq,curs)
			cars.extend(car)
	for car in cars: # car is remaining car capacity, carid, cardateid but also legid
		try:
			carlegs[car[1]].append((car[3],car[0]))
		except KeyError:
			carlegs[car[1]] = [(car[3],car[0])]
		carid = car[1]
		carcap = car[0]
		cdid = car[2]
		if not carid in mincap.keys():
			mincap[carid] = carcap
		elif carcap < mincap[carid]:
			mincap[carid] = carcap
		capacity = mincap
	return (mincap,legs,carlegs)

def getcities(legid,curs):
	getcitiesq = "SELECT startcity,endcity FROM legedgeindex WHERE legid=%s" % legid
	curs.execute(getcitiesq)
	return curs.fetchone()

def trainman(startcity,endcity,trainid,date,curs,year=1967,westbound=True):
	mincap, legs, carlegs = getcaps(startcity,endcity,trainid,date,westbound,'99','A',curs)
	if len(carlegs) > 10:
		return (1,"INVTO")
	legnames = []
	outstr = '     '
	for leg in range(0,len(legs)):
		names = getcities(legs[leg],curs)
		outstr += names[0]
		outstr += "  "
		if leg == len(legs)-1:
			outstr += names[1]
	outstr += "\n"
	for car in carlegs.keys():
		outstr += car
		outstr += "   "
		for leg in carlegs[car]:
			outstr += pad(str(leg[1]),2)
			outstr += "   " # eventuallly sometimes a slash
		outstr += "\n"
	return (0,outstr[:-1])

def query(carcode,trainid,date,startcity,endcity,reqseats,accomreq,curs,year=1967,westbound=True):
	mincap,legs = getcaps(startcity,endcity,trainid,date,westbound,carcode,accomreq,curs)[0:2]
	datstr = doy2monthdate(year,date)
	foundcar = ''
	carfound = False
	totalmincap = sum(mincap.values())
	for car in mincap.keys():
		capacity = mincap[car]
		if capacity > reqseats:
			carfound = True
			foundcar = car
			outstr = 'AV%s%s' % (pad(str(totalmincap),3),datstr)
			return (carfound,foundcar,outstr,legs)
	if not carfound:
		return (carfound,mincap)

def findspecificcardates(legid,carid,curs):
	grabq = "SELECT id FROM cardates WHERE legid=%s AND carid='%s';" % (legid,carid)
	curs.execute(grabq)
	return curs.fetchone()[0]

def makelegreservation(resid,cardateid,curs):
	insertq = "INSERT INTO legreservations(reservationid,cardateid) VALUES (%s,%s) RETURNING id;" % (resid,cardateid)
	curs.execute(insertq)
	response = curs.fetchone()[0]
	return response

def makereservation(date,carid,seats,startcity,endcity,curs):
	resq = '''INSERT INTO reservations(date,car,seats,startcity,endcity) 
		VALUES ('%s','%s',%s,'%s','%s') RETURNING id;''' \
		% (date,carid,seats,startcity,endcity)
	curs.execute(resq)
	resid = curs.fetchone()[0]
	return resid

def reserve(carid,legs,seats,startcity,endcity,date,curs,year=1967):
	try:
		resid = makereservation(date,carid,seats,startcity,endcity,curs)
		for leg in legs:
			cardate = findspecificcardates(leg,carid,curs)
			makelegreservation(resid,cardate,curs)
		ts = timestmp()
		dt = doy2monthdate(year,date)
		outstr = "OK%s %s %s" % (carid,dt, ts)
		return (0,outstr)
	except Exception as e:
		print(str(e))
		return (1)

if __name__ == "__main__":
	cur = conn.cursor()
	#cur.execute("SELECT * FROM trains")
	#print(cur.fetchone())
	request = sys.argv[1].upper()
	if len(request) != 18 and len(request) != 13:
		print("usage: script.py RASLPDLPNSTRNCNCDT")
	elif len(request) == 18: # normal card
		requesttype = request[0]
		accomreq = request[1]
		startlegp = request[2:5]
		destlegp = request[5:8]
		numseats = int(request[8:10])
		trainid = request[10:13]
		carcode = request[13:15]
		date = request[15:18]
		if requesttype == "Q":
			carquery = query(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,cur)
			if carquery[0]:
				print(carquery[2])
		elif requesttype == "R": # reservation time
			carquery = query(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,cur)
			if carquery[0]:
				reservation = reserve(carquery[1],carquery[3],numseats,startlegp,destlegp,date,cur)
				if reservation[0] == 0:
					conn.commit()
					print(reservation[1])
		elif requesttype == "K":
			cancellation = cancel(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,cur)
			if cancellation[0] == 0:
				conn.commit()
				print(cancellation[1])
			else:
				print(cancellation[1])
	else: # supervisor card
		requesttype = request[0]
		startcity = request[1:4]
		endcity = request[4:7]
		trainid = request[7:10]
		date = request[10:13]
		if requesttype == "T":
			manifest = trainman(startcity,endcity,trainid,date,cur)
			print(manifest[1])

