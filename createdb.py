import sqlite3

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

def createdb(schemafile,data,dbname,prompt=True):
    if prompt:
        cont = input("This will delete %s, are you sure? " % dbname)
        if cont[0].lower()!="y":
            return 1
    # wipe the file
    with open(dbname,"w") as f:
        f.write("")
    conn = sqlite3.connect(dbname)
    curs = conn.cursor()

    # read da file
    with open(schemafile,"r") as f:
        schema = f.read()

    # write da schema
    curs.executescript(schema)
    conn.commit()

    if prompt:
        cont = input("Write all trains and routes from %s? " % data)
        if cont[0].lower()!='y':
            return 0
    
    # read trains
    trains = []

    with open(data,"r") as f:
        s = f.readline()
        # go past header
        s = f.readline()
        while s != '' and s != '\n':
            sp = s[:-1].split(',')
            trains.append(train(sp[0],sp[1],sp[2],sp[3],sp[4]))
            s = f.readline()
    if prompt:
        print("The following trains were loaded from the file")
        for x in trains:
            print(x)
    
    


if __name__ == "__main__":
    createdb("sqliteschema.sql","1967trains.csv","db.sqlite3",prompt=False)