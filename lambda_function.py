import psycopg2
import json
import sys
from datetime import datetime,UTC
import configparser
import os

# custom exceptions
class LegClosed(Exception):
	pass

def doy2monthdate(year,day):
	date_string = "%s %s" % (year,day)
	date_object = datetime.strptime(date_string, '%Y %j')
	return date_object.strftime('%b%d').upper()

def timestmp():
	now = datetime.now(UTC)
	formatted_time = now.strftime("%j/%H%M")
	return formatted_time.upper()

def pad(num,spaces):
	tnum = str(num)
	while len(tnum)<spaces:
		tnum = "0" + tnum
	return tnum

def findcars(legid,accomtype,curs):
	if accomtype != 'A':
		findcarsq = "SELECT remcap, carid, id, trainid, closed FROM cardatetrain WHERE legid=%s AND accomtype='%s';" % (legid, accomtype)
	else:
		findcarsq = "SELECT remcap, carid, id, trainid, closed FROM cardatetrain WHERE legid=%s;" % (legid)
	curs.execute(findcarsq)
	foundcars = curs.fetchall()
	return foundcars

def fetchcar(legid,carcode,accomtype,curs,remcap=True):
	foundcars = findcars(legid,accomtype,curs)
	matchedcar = ''
	if carcode not in ["00"]: # not a control code, ergo they want a specific car
		outlst = []
		for car in foundcars:
			if remcap: # remaining capacity, probably all we care about
				usage = car[0]
			else:
				raise NotImplementedError
			if carcode == '99':
				outlst.append((usage,car[1],car[2],legid,car[4]))
			elif car[1].endswith(carcode):
				outlst.append((usage,car[1],car[2],legid,car[4]))
		return outlst
	else:
		raise NotImplementedError


def queryleg(legid, carcode,accomtype, curs):
	fetchedcars = fetchcar(legid,carcode,accomtype,curs,remcap=True)
	return fetchedcars

def findedges(startcity,endcity,trainid,curs):
	wb = getdirection(startcity,endcity,curs)
	startindexq = "SELECT index FROM citiesmain WHERE mnemonic='%s';" % startcity
	endindexq = "SELECT index FROM citiesmain WHERE mnemonic='%s';" % endcity
	curs.execute(startindexq)
	startindex = curs.fetchone()[0]
	curs.execute(endindexq)
	endindex = curs.fetchone()[0]
	if wb:
		comp = "<="
	else:
		comp = ">="
	findedgesq = '''SELECT edgeid 
	FROM trainedgesindex 
	WHERE %s %s startindex 
	AND endindex %s %s 
	AND trainid='%s';''' % \
		(startindex,comp,comp,endindex,trainid)
	curs.execute(findedgesq)
	edges = curs.fetchall()
	outedges = []
	for edge in edges:
		outedges.append(edge[0])
	return outedges

def findroutelegs(startleg,endleg,curs,westbound=True):
	fetchstartq = "SELECT startindex, date, dayoftrain, trainid FROM legedgeindex WHERE legid=%s;" % startleg
	curs.execute(fetchstartq)
	startindex, date, dayoftrain, trainid = curs.fetchall()[0]
	fetchendq = "SELECT endindex FROM legedgeindex WHERE legid=%s;" % endleg
	curs.execute(fetchendq)
	endindex = curs.fetchone()[0]
	if westbound:
		sort = "ASC"
		comp = "<="
	else:
		sort = "DESC"
		comp = ">="
	findorderedq = '''SELECT legid, closed 
		FROM legedgeindex 
		WHERE %s %s startindex 
		AND endindex %s %s 
		AND trainid='%s' 
		AND date - dayoftrain = %s
		ORDER BY startindex %s;''' % (startindex,comp,comp,endindex,trainid,date-dayoftrain,sort)
	curs.execute(findorderedq)
	legs = curs.fetchall()
	outlegs = []
	for leg in legs:
		outlegs.append(leg)
	return outlegs

def closeleg(legid,curs):
	closeq = "UPDATE legs SET closed = true WHERE id = %s" % legid
	curs.execute(closeq)
	return 0

def close(startcity,endcity,trainid,date,curs,year=1967):
	ts = timestmp()
	tdiff = int(ts[0:3]) - int(date)
	if tdiff > 7 or tdiff < 0:
		return (1,"INVDTE")
	westbound = getdirection(startcity,endcity,curs)
	extremelegs = findextremelegs(startcity,endcity,trainid,date,westbound,curs)
	legs = findroutelegs(extremelegs[0][0],extremelegs[1][0],curs,westbound=westbound)
	dt = doy2monthdate(year,date)
	for leg in legs:
		closeleg(leg[0],curs)
	outstr = "XX%s %s %s" % (trainid,dt, ts)
	return (0,outstr)


def findextremelegs(startcity,endcity,trainid,date,westbound,curs):
	if westbound:
		sortdir = "ASC"
	else:
		sortdir = "DESC"
	findstartlegq = '''SELECT legid, date, startcity, endcity, startindex, dayoftrain
			FROM legedgeindex 
			WHERE startcity='%s' 
			AND trainid='%s' 
			AND date = %s 
			ORDER BY startindex %s;''' \
			% (startcity,trainid,date,sortdir)
	curs.execute(findstartlegq)
	foundlegs = [curs.fetchone()]
	dayoftrain = foundlegs[0][5]
	findendlegq = '''SELECT legid, date, startcity, endcity, startindex
			FROM legedgeindex 
			WHERE endcity='%s' 
			AND trainid='%s' 
			AND date - dayoftrain + %s = %s 
			ORDER BY startindex %s;''' \
			% (endcity,trainid,dayoftrain,date,sortdir)
	curs.execute(findendlegq)
	foundlegs.append(curs.fetchone())
	return foundlegs

def cancel(carcode,trainid,date,startcity,endcity,reqseats,accomreq,curs,year=1967,westbound=True):
	if carcode in ['00','99']:
		return [2,"INVCAR"] # can't be a control code
	# find a car ID
	extremelegs = findextremelegs(startcity,endcity,trainid,date,westbound,curs)
	legs = findroutelegs(extremelegs[0][0],extremelegs[1][0],curs,westbound=westbound)
	carid = fetchcar(extremelegs[0][0],carcode,accomreq,curs)
	for leg in legs:
		restorinv(reqseats,carcode,leg[0],curs)
	ts = timestmp()
	dt = doy2monthdate(year,date)
	outstr = "CL%s%s %s %s" % (trainid,carcode,dt, ts)
	return (0,outstr)

def getcaps(startcity,endcity,trainid,date,carcode,accomreq,curs):
	westbound=getdirection(startcity,endcity,curs)
	foundlegs = findextremelegs(startcity,endcity,trainid,date,westbound,curs)
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
		for leg in legs:
			legid = leg[0]
			car = queryleg(legid,carcode,accomreq,curs)
			cars.extend(car)
	for car in cars: # car is remaining car capacity, carid, cardateid but also legid
		try:
			carlegs[car[1]].append((car[3],car[0],car[4]))
		except KeyError:
			carlegs[car[1]] = [(car[3],car[0],car[4])]
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

def getindex(city,curs):
	getcityvaluesq = "SELECT index FROM citiesmain WHERE mnemonic='%s'" % city
	curs.execute(getcityvaluesq)
	index = curs.fetchone()
	if index == '':
		raise ValueError
	else:
		return int(index[0])

def getdirection(startcity,endcity,curs):
	sindex = getindex(startcity,curs)
	eindex = getindex(endcity,curs)
	if eindex - sindex >= 0: # default to westbound
		return True
	else:
		return False

def createorconfirmtrain(trainid,startcity,endcity,curs):
	fetchtrainq = "SELECT * FROM trains WHERE id='%s'" % trainid
	curs.execute(fetchtrainq)
	trains = curs.fetchall()
	if len(trains) == 0:
		wb = getdirection(startcity,endcity,curs)
		createtrainq = "INSERT INTO trains(id,westbound) VALUES ('%s',%s);" % (trainid,wb)
		curs.execute(createtrainq)
	return

def findlegbyedge(edge,trainid,date,curs):
	findlegq = "SELECT id FROM legs WHERE trainid='%s' AND edgeid=%s AND date='%s';" % (trainid,edge,date)
	curs.execute(findlegq)
	legs = curs.fetchall()
	return legs

def checkormakelegs(edges,trainid,date,curs):
	stublegq = "INSERT INTO legs(trainid,edgeid,date,dayoftrain,closed) VALUES "
	legs = []
	tomake = 0
	for edge in edges:
		idate = int(date)
		dayoftrain = 0 #someday need to handle this
		convdate = pad(idate + dayoftrain,2)
		leg = findlegbyedge(edge,trainid,convdate,curs)
		if len(leg) == 0: # no legs 
			stublegq += "('%s',%s,'%s',0,false)," % (trainid,edge,date)
			tomake += 1
		elif len(leg) == 1: # we expect this
			legs.append(leg[0][0])
		else: # too many legs
			raise ValueError
	if tomake > 0:
		curs.execute(stublegq[:-1] + " RETURNING id;")
	for x in curs.fetchall(): # I can't remember if python hates extending with a tuple
		legs.append(x[0])
	return legs

def makecardates(legs,carid,accomtype,seats,curs):
	stubcdateq = "INSERT INTO cardates(legid,carid,accomtype,remcap) VALUES "
	for leg in legs:
		stubcdateq += "(%s,'%s','%s',%s)," % (leg,carid,accomtype,seats)
	curs.execute(stubcdateq[:-1] + ";")
	return

def equip(startcity,endcity, trainid, carcode, accomtype, seats, date, curs,year=1967):
	try:
		createorconfirmtrain(trainid,startcity,endcity,curs)
	except TypeError: # the city doesn't exist
		return (1,"INVCITY")
	# need to make legs now
	try:
		edges = findedges(startcity,endcity,trainid,curs)
	except NotFoundError:
		return (1,"INVCITY")
	legs = checkormakelegs(edges,trainid,date,curs)
	try:
		carid = trainid + carcode
		makecardates(legs,carid,accomtype,seats,curs)
		ts = timestmp()
		dt = doy2monthdate(year,date)
		outstr = "EQ%s %s %s %s" % (seats,carid,dt, ts)
		return (0,outstr)
	except Exception as e:
		if 'duplicate' in str(e).lower():
			return(2,"INVCAR")
		else:
			return (3,str(e))

def trainman(startcity,endcity,trainid,date,curs,year=1967,westbound=True):
	mincap, legs, carlegs = getcaps(startcity,endcity,trainid,date,'99','A',curs)
	if len(carlegs) > 10:
		return (1,"INVTO")
	legnames = []
	outstr = '     '
	for leg in range(0,len(legs)):
		names = getcities(legs[leg][0],curs)
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
			if not leg[2]: # if the leg isn't closed
				outstr += "   "
			else: # it is
				outstr += "/  "
		outstr += "\n"
	return (0,outstr[:-1])

def query(carcode,trainid,date,startcity,endcity,reqseats,accomreq,curs,year=1967):
	mincap,legs = getcaps(startcity,endcity,trainid,date,carcode,accomreq,curs)[0:2]
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
	grabq = "SELECT id, closed FROM cardatetrain WHERE legid=%s AND carid='%s';" % (legid,carid)
	curs.execute(grabq)
	cardate = curs.fetchone()
	if cardate[1]:
		raise LegClosed(str(cardate[0]))
	return cardate[0]

def makelegreservation(seats,cardateid,legid,curs):
	updateq = "UPDATE CARDATES SET remcap = remcap - %s WHERE id = %s AND legid = %s;" % (seats,cardateid,legid)
	curs.execute(updateq)
	return 0

def restorinv(seats,carcode,legid,curs):
	updateq = "UPDATE CARDATES SET remcap = remcap + %s WHERE RIGHT(carid,2) = '%s' AND legid = %s RETURNING remcap;" % (seats,carcode,legid)
	curs.execute(updateq)
	remcap = curs.fetchone()[0]
	return [0,remcap]

def reserve(carid,legs,seats,date,curs,year=1967):
	try:
		for leg in legs:
			cardate = findspecificcardates(leg[0],carid,curs)
			makelegreservation(seats,cardate,leg[0],curs)
		ts = timestmp()
		dt = doy2monthdate(year,date)
		outstr = "OK%s %s %s" % (carid,dt, ts)
		return (0,outstr)
	except LegClosed:
		return(1,"INVDTE")
	except Exception as e:
		return (2,str(e))


def parse_n_route_string(string,curs):
	if len(string) != 18 and len(string) != 13:
		return "usage: script.py RASLPDLPNSTRNCNCDT"
	elif len(string) == 18: # normal card
		stringtype = string[0]
		accomreq = string[1]
		startlegp = string[2:5]
		destlegp = string[5:8]
		numseats = int(string[8:10])
		trainid = string[10:13]
		carcode = string[13:15]
		date = string[15:18]
		if stringtype == "Q":
			carquery = query(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,curs)
			if carquery[0]:
				return carquery[2]
		elif stringtype in ["R","D"]: # reservation time
			carquery = query(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,curs)
			if carquery[0]:
				reservation = reserve(carquery[1],carquery[3],numseats,date,curs)
				if reservation[0] == 0:
					conn.commit()
				return reservation[1]
		elif stringtype in ["K","A"]:
			cancellation = cancel(carcode,trainid,date,startlegp,destlegp,numseats,accomreq,curs)
			if cancellation[0] == 0:
				conn.commit()
			return cancellation[1]
		elif stringtype =="E":
			result = equip(startlegp,destlegp,trainid,carcode,accomreq,numseats,date,curs)
			if result[0] == 0:
				conn.commit()
			return result[1]
	else: # supervisor card
		stringtype = string[0]
		startcity = string[1:4]
		endcity = string[4:7]
		trainid = string[7:10]
		date = string[10:13]
		if stringtype == "T":
			manifest = trainman(startcity,endcity,trainid,date,curs)
			return manifest[1]
		elif stringtype == "X":
			closeout = close(startcity,endcity,trainid,date,curs)
			if closeout[0] == 0:
				conn.commit()
			return closeout[1]

def lambda_handler(event, context): # we are in a lambda
	db = os.environ.get('db')
	user = os.environ.get('dbuser')
	ps = os.environ.get('dbpass')
	url = os.environ.get('url')
	conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (url,db,user,ps))
	cur = conn.cursor()
	request = event["query"].upper()
	response = parse_n_route_string(request,cur)
	return {
		'statusCode': 200,
		'body': json.dumps(response)
	}


if __name__ == "__main__": # we're not in a lambda anymore
	# fetch the config
	config = configparser.ConfigParser()
	config.read("reservations.ini")
	db = config['DEFAULT']['db']
	user = config['DEFAULT']['user']
	ps = config['DEFAULT']['ps']

	# set up the db connection
	conn = psycopg2.connect("dbname=%s user=%s password=%s" % (db,user,ps))

	cur = conn.cursor()
	request = sys.argv[1].upper()
	print(parse_n_route_string(request,cur))
