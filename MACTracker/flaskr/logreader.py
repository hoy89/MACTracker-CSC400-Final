import time
import paramiko
import threading
import os
import sys
import dateutil.parser
import unicodedata
import sqlite3
from flask import Flask, current_app
from flaskr import db
from flaskr.db import get_db
import warnings
warnings.filterwarnings(action='ignore',module='.*paramiko.*')

threads = []
connectFailedNodes = []

def readLog(sftpClient, nodeName, areaName, liveInterval, app):
	print("Logging started on " + nodeName)
	remoteFile = sftpClient.open('/home/pi/probemon.log')
	while True:
		where = remoteFile.tell()
		line = remoteFile.readline()
		if not line:
			time.sleep(0.100)
			remoteFile.seek(where)
		else:
			line = parseLogOutput(line)
			writeDatabase(line, nodeName, areaName, liveInterval, app)
		    
def writeDatabase(line, nodeName, areaName, liveInterval, app):
	print("Writing to database. Source node: " + nodeName)
	line[0] = line[0].decode('UTF8')
	line[1] = line[1].decode('UTF8')
	line[2] = line[2].decode('UTF8')

	macAddress = line[0]
	deviceType = line[1]
	detectedNetwork = line[2]
	lastDetectTime = line[3]
	lastDetectDate = line[4]

	with app.app_context():
		db = get_db()
		cursor = db.cursor()
		cursor.execute("SELECT macAddress FROM macAddressPool WHERE macAddress = ?", (line[0],))
		data=cursor.fetchone()
		if data is None:
			db.execute(
				'INSERT INTO macAddressPool (macAddress, deviceType, nodeName, lastDetectTime, lastDetectDate, timeSpentLive, live, detectionCount, areaName)'
				' VALUES (?,?,?,?,?,?,?,?,?)',
				(macAddress, deviceType, nodeName, lastDetectTime, lastDetectDate,liveInterval, True, 1, areaName)
			)
		else:
			rows = db.execute(
				'SELECT lastDetectTime, lastDetectDate, detectionCount, live, previousAliveDate, lastAliveTime, timeSpentLive, previousArea, previousNode, nodeName, areaName FROM macAddressPool WHERE macAddress = ?', (line[0],)
			).fetchall()

			lastDetectTimeOld = rows[0][0]
			lastDetectDateOld = rows[0][1]
			detectionCount = int(rows[0][2])
			live = rows[0][3]
			previousAliveDate = rows[0][4]
			lastAliveTime = rows[0][5]
			timeSpentLive = rows[0][6]
			previousArea = rows[0][7]
			previousNode = rows[0][8]
			newPreviousNode = rows[0][9]
			newPreviousArea = rows[0][10]

			# misc
			detectionCount = detectionCount + 1

			# cosmetics
			if detectedNetwork == '':
				detectedNetwork = None

			if live == False:
				# update previous values
				previousAliveDate = lastDetectDateOld
				lastAliveTime = lastDetectTimeOld
				previousArea = newPreviousArea
				previousNode = newPreviousNode

			if live == True:
				if lastAliveTime is None:
					timeSpentLive = liveInterval
				else:
					currentTime = line[3]
					previousTime = lastAliveTime

					currentTime = int(currentTime[-2:])
					previousTime = int(previousTime[-2:])
					timeSpentLive = abs(currentTime - previousTime)

			db.execute(
				'UPDATE macAddressPool SET deviceType=?, nodeName=?, areaName=?, lastDetectTime=?, lastDetectDate=?, previousAliveDate=?, lastAliveTime=?, live=?, detectionCount=?, previousNode=?, previousArea=?, detectedNetwork=?, timeSpentLive=? WHERE macAddress=?',
				 [deviceType, nodeName, areaName, lastDetectTime, lastDetectDate, previousAliveDate, lastAliveTime, True, detectionCount, previousNode, previousArea, detectedNetwork, timeSpentLive, line[0]])
		db.commit()


def parseLogOutput(line):
	line = line.split('\t')
	date = dateutil.parser.parse(line[0])
	del line[0]
	line[2] = line[2].rstrip('\n')
	newLine = [item.encode('UTF8') for item in line]
	newLine.append(str(date.time())[0:5])
	newLine.append(str(date.date()))
	return newLine

def connectNode(client_name, user, passw):
	print("Connecting...")
	connectAttempts = 3
	errorFlag = 0
	sftpClient = None
	sshClient = None

	while connectAttempts > 0:
		try:
			connectAttempts = connectAttempts - 1
			sshClient = paramiko.SSHClient()
			sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			sshClient.connect(client_name, username=user, password=passw)
			sftpClient = sshClient.open_sftp()
			return sftpClient, sshClient, errorFlag
		except:
			print("Connection failed. Trying again...")

	errorFlag = 1
	return sftpClient, sshClient, errorFlag


def startNodeLogging(sshClient):
	print("Starting node logging...")
	stdin_, stdout_, stderr_ = sshClient.exec_command("sudo pkill -9 -f probemon.py") #kill any previous script first
	stdin_, stdout_, stderr_ = sshClient.exec_command("sudo rm /home/pi/probemon.log") #remove old log before starting up logging
	stdin_, stdout_, stderr_ = sshClient.exec_command("sudo touch /home/pi/probemon.log") #create new log file
	stdin_, stdout_, stderr_ = sshClient.exec_command("sudo airmon-ng start wlan1") #enable monitor mode on wlan1
	stdout_.channel.recv_exit_status() #wait until previous command finishes
	stdin_, stdout_, stderr_ = sshClient.exec_command("sudo python /home/pi/python/probemon/probemon.py -i wlan1mon -f -s") #start monitoring
	time.sleep(5)

def connectAndLog(nodeIP, nodeName, areaName, nodeUser, nodePass, liveInterval, app):
	print("Attempting to connect to " + nodeName + ".")
	sftpClient, sshClient, errorFlag = connectNode(nodeIP, nodeUser, nodePass)

	if errorFlag == 0:
		startNodeLogging(sshClient)
		readLog(sftpClient, nodeName, areaName, liveInterval, app)
	else:
		print("Could not connect to " + nodeName + ".")


def startNodes(app, nodeUser, nodePass, liveInterval):
	with app.app_context():
		started = False
		print("Starting node check.")
		while started != True:
			db = get_db()
			rows = db.execute(
				'SELECT nodeIP, nodeName, areaName FROM nodes'
			).fetchall()

			if rows != []:
				print("Processing nodes.")
				nodes = []
				for row in rows:
					nodes.append(row)

				for node in nodes:
					nodeIP = str(node[0])
					nodeName = str(node[1])
					areaName = str(node[2])

					print("Starting a thread.")
					t = threading.Thread(target=connectAndLog, args=(nodeIP, nodeName, areaName, nodeUser, nodePass, liveInterval, app,))
					t.dameon = True
					threads.append(t)
					t.start()
				started = True
			time.sleep(5)

		print("Finished loading nodes. Scanning for changes...")
		while True:
			previousRows = rows

			db = get_db()
			rows = db.execute(
				'SELECT nodeIP, nodeName, areaName FROM nodes'
			).fetchall()

			if rows != previousRows:
				if rows != []:
					print("Processing new nodes.")
					nodes = []
					for row in rows:
						if row not in previousRows:
							nodes.append(row)
					if nodes != []:
						for node in nodes:
							nodeIP = str(node[0])
							nodeName = str(node[1])
							areaName = str(node[2])

							print("Starting a thread.")
							t = threading.Thread(target=connectAndLog, args=(nodeIP, nodeName, areaName, nodeUser, nodePass, liveInterval, app,))
							t.dameon = True
							threads.append(t)
							t.start()
			time.sleep(5)



def main(app, nodeUser, nodePass, liveInterval):
	print("Starting Log Reader.")
	t = threading.Thread(target=startNodes, args=(app, nodeUser, nodePass, liveInterval,))
	t.dameon = True
	threads.append(t)
	t.start()	

if __name__ == "__main__":
    main()
