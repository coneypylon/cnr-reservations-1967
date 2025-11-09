import psycopg2
import json
import sys
from datetime import datetime,UTC
import configparser
import os
from reservations import parse_n_route_string, LegClosed

def lambda_handler(event, context): # we are in a lambda
	db = os.environ.get('db')
	user = os.environ.get('dbuser')
	ps = os.environ.get('dbpass')
	url = os.environ.get('url')
	conn = psycopg2.connect("host=%s dbname=%s user=%s password=%s" % (url,db,user,ps))
	cur = conn.cursor()
	try:
		request = event["query"].upper()
	except KeyError:
		rawrequest = json.loads(event["body"])
		request = rawrequest["query"].upper()
	print(request)
	response = parse_n_route_string(request,cur,conn)
	cur.close()

	return {
		'statusCode': 200,
		"headers": {
			"Content-Type": "application/json",
			"Access-Control-Allow-Origin": "*",
			"Access-Control-Allow-Methods": "OPTIONS,POST",
			"Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token"
		},
		'body': json.dumps(response)
	}

