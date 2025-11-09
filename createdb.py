import sqlite3

def parsedestinations(routestr):
    

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
    
    # read train routes
    trains = []

    with open(data,"r") as f:
        s = f.readline()
        s = f.readline() # skip header
        while s != '' and s != '\n':
            trains.append(s[:-1].split(','))
            s = f.readline()
    
    # we assume the set of trains is well-formed.
    for train in trains:


if __name__ == "__main__":
    createdb("sqliteschema.sql","1967trains.csv","db.sqlite3",prompt=False)