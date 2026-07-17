import sqlite3
from reservations import equip
import datetime

def tqdm_no_op(iterable, *args, **kwargs):
    """Dummy function to replace tqdm when it is not installed."""
    return iterable

try:
    # Attempt to import the real tqdm progress bar library
    from tqdm import tqdm
except ImportError:
    # If the import fails, use the dummy function instead
    tqdm = tqdm_no_op
    print("tqdm not found. Running without a progress bar.")
except Exception as e:
    # Handle other potential errors during import if necessary
    tqdm = tqdm_no_op
    print(f"An unexpected error occurred during tqdm import: {e}. Running without a progress bar.")

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

def findorcreateedge(edge,curs):
    try:
        findedgeq = "SELECT id FROM edges WHERE startcity='%s' AND endcity='%s';" % edge
        curs.execute(findedgeq)
        edgeid = curs.fetchone()[0]
    except TypeError: # it doesn't exist
        createedgeq = "INSERT INTO edges(startcity,endcity) VALUES ('%s','%s') RETURNING id;" % edge
        curs.execute(createedgeq)
        edgeid = curs.fetchone()[0]
    return edgeid

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
        self.start = self.route[0][0]
        self.end = self.route[-1][1]
        self.cars = readcars(trainid,"Z",coaches)
        self.cars.extend(readcars(trainid,"Y",clubs))
    def __str__(self):
        outstr = "Train %s, runs %s, from  %s to %s, %s cars" % (self.id,self.days,self.route[0][0],self.route[len(self.route)-1][1],len(self.cars))
        return outstr
    def create(self,curs):
        # this assumes that the db is empty, and that there is only one of each train
        createtrainq = "INSERT INTO trains('id') VALUES ('%s')" % self.id
        curs.execute(createtrainq)
        edges = []
        for routeedge in self.route:
            edges.append(findorcreateedge(routeedge,curs))
        instedgeq = "INSERT INTO trainedges(trainid,edgeid) VALUES "
        for edge in edges:
            newq = "('%s',%s)," % (self.id,edge)
            instedgeq += newq
        curs.execute(instedgeq[:-1] + ";")

def gendates(days,year=1967):
    valid_dows = []

    for x in range(0,7):
        if days[x].lower() == 'y':
            valid_dows.append(x)
    
    currentday = datetime.date(year,1,1)
    endday = datetime.date(year + 1,1,1)
    oneday = datetime.timedelta(days=1)

    dates = []

    while currentday != endday:
        dow_index = int(currentday.strftime('%w'))
        if dow_index in valid_dows:
            doy = currentday.timetuple().tm_yday
            dates.append(doy)
        currentday += oneday
    return dates

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
        cont = input("Write all above trains and routes from %s? " % data)
        if cont[0].lower()!='y':
            return 0
    for x in trains:
        x.create(curs)
        conn.commit()
    
    if prompt:
        cont = input("Insert all car records from %s trains (This will take a while)? " % len(trains))
        if cont.lower()[0] != 'y':
            return 0
    for tr in trains:
        for car in tqdm(tr.cars,desc="Train %s" % tr.id):
            dates = gendates(tr.days)
            for day in dates:
                equip(tr.start,tr.end,tr.id,car.carnum,car.type,car.capacity,day,curs)
            conn.commit()




if __name__ == "__main__":
    createdb("sqliteschema.sql","1967trains.csv","db.sqlite3")
