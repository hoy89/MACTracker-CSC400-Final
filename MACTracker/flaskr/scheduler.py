import time
import paramiko
import threading
import os
import sys
import dateutil.parser
import unicodedata
import sqlite3
import datetime
from flask import Flask, current_app
from flaskr import db
from flaskr.db import get_db

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

threads = []
def updateLive(app, liveInterval, refreshSpeed):
	with app.app_context():
		db = get_db()
		print("Starting live status update.")
		while True:
			macAddressPool = db.execute(
				'SELECT macAddress, lastDetectTime, live, lastAliveTime, timeSpentLive FROM macAddressPool'
			).fetchall()

			for macAddress in macAddressPool:
				mac = macAddress[0]
				live = macAddress[2]

				if live == True:
					currentTime = macAddress[1]
					currentTime = (int(currentTime[:2]) * 60) + int(currentTime[-2:])

					# Get current system time in minutes starting from 0
					date = dateutil.parser.parse(datetime.datetime.now().isoformat())
					systemTime = str(date.time())[0:5]
					systemTime = (int(systemTime[:2]) * 60) + int(systemTime[-2:])

					if abs((currentTime - systemTime)) > liveInterval:
						db.execute('UPDATE macAddressPool SET live=? WHERE macAddress=?', [False, mac])
				db.commit()
			time.sleep(refreshSpeed)

def main(app, liveInterval, refreshSpeed):
	print("Starting Scheduler.")
	t = threading.Thread(target=updateLive, args=(app, liveInterval, refreshSpeed)) #node_combined[0] is ip, [1] is name
	t.dameon = True
	threads.append(t)
	t.start()

if __name__ == "__main__":
	main()
