
'''
trainid,days,route,coaches,clubs
001,YYYYYYY,MTLOTTPEMNBYCPLHPNLLCARMSLKMKIWPGPLPRIVMVLWATSASBIGWAIEDMEDSHINJASBLRKAMBBACHKVAN,017602760376044>
005,YYYYYYY,MTLOTTPEMNBYCPLHPNLLCARMSLKMKIWPGPLPRIVMVLWATSASBIGWAIEDMEDSHINJASBLRKAMBBACHKVAN,06760246,
'''

import sqlite3
import sys

# class helpers
def readcars(trainid,type,carstring):
	outlst = []
	if len(carstring) < 4:
		return outlst
	for x in range(0,len(carstring),4):
		carnum = carstring[x:x+2]
		capacity = carstring[x+2:x+4]
		outlst.append(car(trainid,carnum,type,capacity))
	return outlst

def convroutes(routestr):
	outlst = []
	for x in range(0,len(routestr)-3,3):
		outlst.append((routestr[x:x+3],routestr[x+3:x+6]))
	return outlst

class car:
	def __init__(self,trainid,carnum,type,capacity):
		self.trainid = trainid
		self.carnum = carnum
		self.id = trainid + carnum
		self.type = type
		self.capacity = int(capacity)

class train:
	def __init__(self,trainid,days,route,coaches,clubs):
		self.id = trainid
		self.days = days
		self.route = convroutes(route)
		self.coaches = readcars(trainid,"Z",coaches)
		self.clubs = readcars(trainid,"Y",clubs)
	def __str__(self):
		outstr = "Train %s, runs %s, from  %s to %s, %s coaches, %s club cars" % (self.id,self.days,self.route[0][0],self.route[len(self.route)-1][1],len(self.coaches),len(self.clubs))
		return outstr

def checkormakeedge(edge,curs):
	findedgeq = "SELECT id FROM edges WHERE startcity = %s AND endcity = %s" % (edge[0],edge[1])
	curs.execute(findegeq)
	result = curs.fetchone()

def sqlify(dbname,trains):

def prepDB(filename,dbname):
	trains = []
	with open(filename,"r") as f:
		s = f.readline()
		# go past header
		s = f.readline()
		while s != '' and s != '\n':
			sp = s[:-1].split(',')
			trains.append(train(sp[0],sp[1],sp[2],sp[3],sp[4]))
			s = f.readline()
	print("The following trains were loaded from the file")
	for x in trains:
		print(x)
	consent = input("Replace database '%s' with the %s trains and routes from %s?" % (dbname, len(trains), filename))
	if consent[0].lower() == 'y':
		with open(dbname,'w') as g:
			g.write('')
		sqlify(dbname,trains) 

if __name__ == '__main__':
	prepDB(sys.argv[1],sys.argv[2])
