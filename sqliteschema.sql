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
  CONSTRAINT unqedges UNIQUE("startcity","endcity")
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

INSERT INTO "citiesmain" ("idex", "mnemonic", "commonname") VALUES
(30, 'AMH', 'Amherst'),
(230, 'ARM', 'Armstrong'),
(400, 'BBA', 'Boston Bar'),
(320, 'BIG', 'Biggar'),
(147, 'BKL', 'Brockville'),
(380, 'BLR', 'Blue River'),
(60, 'BST', 'Bathhurst'),
(155, 'BVL', 'Belleville'),
(0, 'CGY', 'Calgary'),
(255, 'CHG', 'Chicago'),
(410, 'CHK', 'Chilliwack'),
(165, 'COB', 'Cobourg'),
(200, 'CPL', 'Capreol'),
(70, 'CTN', 'Campbellton'),
(145, 'CWL', 'Cornwall'),
(120, 'DML', 'Drummondville'),
(340, 'EDM', 'Edmonton'),
(350, 'EDS', 'Edson'),
(75, 'GSP', 'Gaspe'),
(0, 'HAM', 'Hamilton'),
(10, 'HFX', 'Halifax'),
(360, 'HIN', 'Hinton'),
(210, 'HPN', 'Horneypayne'),
(370, 'JAS', 'Jasper'),
(390, 'KAM', 'Kamloops'),
(150, 'KGN', 'Kingston'),
(234, 'KIT', 'Kitchener'),
(235, 'LDN', 'London'),
(100, 'LEV', 'Levis'),
(220, 'LLC', 'Longlac'),
(40, 'MCT', 'Moncton'),
(80, 'MJO', 'Mont Joli'),
(250, 'MKI', 'Minaki'),
(140, 'MTL', 'Montreal'),
(290, 'MVL', 'Melville'),
(190, 'NBY', 'North Bay'),
(50, 'NCL', 'Newcastle'),
(0, 'NWR', 'New Westminster'),
(160, 'OTT', 'Ottawa'),
(170, 'PEM', 'Pembroke'),
(0, 'PGO', 'Prince George'),
(270, 'PLP', 'Portage La Prarie'),
(0, 'PRR', 'Prince Rupert'),
(180, 'PSO', 'Parry Sound'),
(110, 'QBC', 'Quebec'),
(90, 'RDL', 'Riviere Du Loup'),
(0, 'REG', 'Regina'),
(280, 'RIV', 'Rivers'),
(245, 'SAR', 'Sarnia'),
(310, 'SAS', 'Saskatoon'),
(0, 'SFY', 'Ste Foy'),
(130, 'SHY', 'St Hyacinthe'),
(0, 'SJN', 'St Johns (NFLD)'),
(240, 'SLK', 'Sioux Lookout'),
(0, 'STC', 'St Catherines'),
(1, 'SYD', 'Sydney'),
(175, 'TOR', 'Toronto'),
(20, 'TRU', 'Truro'),
(420, 'VAN', 'Vancouver'),
(60, 'VIC', 'Victoria'),
(330, 'WAI', 'Wainwright'),
(300, 'WAT', 'Watrous'),
(244, 'WDR', 'Windsor'),
(260, 'WPG', 'Winnipeg');

COMMIT;
