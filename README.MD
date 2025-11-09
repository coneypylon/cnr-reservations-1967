## CNR Electronic Passenger Reservation System (1967) Replica
Python/Postgres implementation

A simple recreation of the 1960s Collins 8401-based reservation system that CN used.

### Setup
1. DB Setup

If running locally, run createdb.py from the command line. There will be a few questions, and then a long wait while it generates the records. There are between 5,000 and 30,000 records to be generated for each train, so I recommend starting the process, saying yes to the prompts until after the prompt that warns you about the time, and then getting a coffee.

2. Config creation

If you want to change the default DB name, make a 'reservations.ini' with contents like the following:

```
[DEFAULT]
db='db.sqlite3'
```

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
