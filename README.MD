## CNR Electronic Passenger Reservation System (1967) Replica
Python/Postgres implementation

A simple recreation of the 1960s Collins 8401-based reservation system that CN used.

### Setup
1. DB Setup

Make a Postgres database that Python can access. You can create a user for it (I did) or just use postgres (obviously not super safe by default)
Once the database is made, use the tables export included in the repo to execute the commands needed to recreate the required schema. Note that it's a dump of my dev database and has a few extra tables not currently used.

2. Config creation

You'll need to make a reservations.ini file with the following contents:

```
[DEFAULT]
db=<YOURDBHERE>
user=<YOURDBUSERHERE>
ps-<YOURDBUSERPASSWORDHERE>
```

Note that the values should be filled based on your setup in #1

3. Operate!

### Usage
This system expects a 14 or 18 column mark-sense card (think Scantron). It has been recreated to expect this as command-line input without spaces.

See the manual (on nboyko.com or in Libraries and Archives Canada) for usage instructions, but there are a few example queries below.

### Examples
#### Equip/Create a train
In the manual, this example takes the format MTLAEZ TORMTL 76 06410 045#

The spaces and extra teleprinter additions are removed and it becomes the below:

```
python main.py EZTORMTL7606410045
```

To which the response should be

```
EQ76 06410 FEB14 DDD/HHMM
```

With DDD/HHMM replaced with the current time UTC.

#### Query a train
As above, extraneous input is removed.

```
python main.py QZTORMTL0506499045
```

Which if you executed these in order should return

```
AV076FEB14
```

Otherwise errors should be as in the manual.
