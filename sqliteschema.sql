BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "cardates" (
	"id"	integer NOT NULL,
	"carid"	character varying(5),
	"legid"	integer,
	"remcap"	integer,
	"accomtype"	character varying(1),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("legid") REFERENCES "legs"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "remcap_nonnegative" CHECK(("remcap" >= 0))
);
CREATE TABLE IF NOT EXISTS "citiesmain" (
	"idex"	integer,
	"mnemonic"	character varying(3) NOT NULL,
	"commonname"	character varying(255)
);
CREATE TABLE IF NOT EXISTS "edges" (
	"id"	integer NOT NULL,
	"startcity"	character varying(3),
	"endcity"	character varying(3),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("endcity") REFERENCES "citiesmain"("mnemonic") ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY("startcity") REFERENCES "citiesmain"("mnemonic") ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "legs" (
	"trainid"	character varying(3),
	"dayoftrain"	integer,
	"id"	integer NOT NULL,
	"edgeid"	integer,
	"date"	integer,
	"closed"	boolean,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("edgeid") REFERENCES "edges"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY("trainid") REFERENCES "trains"("id") ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "linktrains" (
	"mainid"	character varying(3),
	"secondid"	character varying(3),
	"date"	integer,
	FOREIGN KEY("mainid") REFERENCES "trains"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY("secondid") REFERENCES "trains"("id") ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "trainedges" (
	"trainid"	character varying(3) NOT NULL,
	"edgeid"	integer NOT NULL,
	PRIMARY KEY("trainid","edgeid"),
	FOREIGN KEY("edgeid") REFERENCES "edges"("id") ON UPDATE CASCADE ON DELETE CASCADE,
	FOREIGN KEY("trainid") REFERENCES "trains"("id") ON UPDATE CASCADE ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "trains" (
	"id"	character varying(3) NOT NULL,
	"name"	character varying(255),
	"westbound"	boolean,
	PRIMARY KEY("id")
);
CREATE VIEW cardatetrain AS
 SELECT c.id,
    c.carid,
    c.remcap,
    c.legid,
    c.accomtype,
    l.trainid,
    l.closed
   FROM (cardates c
     JOIN legs l ON ((c.legid = l.id)));
CREATE VIEW edgeindex AS
 SELECT e.id AS edgeid,
    e.startcity,
    e.endcity,
    cs.idex AS startindex,
    ce.idex AS endindex
   FROM (edges e
     JOIN citiesmain cs ON e.startcity=cs.mnemonic
     JOIN citiesmain ce ON e.endcity=ce.mnemonic);
CREATE VIEW legcars AS
 SELECT l.id AS legid,
    l.trainid,
    e.startcity,
    e.endcity,
    l.date,
    l.dayoftrain
   FROM (legs l
     LEFT JOIN edges e ON l.edgeid=e.id);
CREATE VIEW legedgeindex AS
 SELECT l.trainid,
    l.dayoftrain,
    l.id AS legid,
    l.edgeid,
    l.date,
    l.closed,
    e.startcity,
    e.endcity,
    e.startindex,
    e.endindex
   FROM (legs l
     JOIN ( SELECT e_1.id AS edgeid,
            e_1.startcity,
            e_1.endcity,
            cs.idex AS startindex,
            ce.idex AS endindex
           FROM (edges e_1
             JOIN citiesmain cs ON e_1.startcity=cs.mnemonic
             JOIN citiesmain ce ON e_1.endcity=ce.mnemonic)) e ON l.edgeid = e.edgeid);
CREATE VIEW trainedgesindex AS
 SELECT t.trainid,
    t.edgeid,
    e.startindex,
    e.endindex
   FROM (trainedges t
     LEFT JOIN edgeindex e ON ((t.edgeid = e.edgeid)));
COMMIT;
