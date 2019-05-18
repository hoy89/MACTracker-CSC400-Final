from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, request
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
import datetime
import random
import string

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    db = get_db()
    macAddressPool = db.execute(
        'SELECT macAddress, deviceType, areaName, nodeName, lastDetectTime, lastDetectDate, previousAliveDate, lastAliveTime, live, timeSpentLive, detectionCount, previousNode, previousArea, detectedNetwork FROM macAddressPool'
    ).fetchall()

    areas = db.execute(
        'SELECT areaName FROM areas'
    ).fetchall()

    nodes = db.execute(
        'SELECT nodeName, areaName FROM nodes'
    ).fetchall()

    timeArray = []
    dateArray = []
    areaArray = []
    liveArray = []
    areaDetectionArray = []
    areaDetectionArrayALT = []
    nodeNameArray = []
    nodeDetectionArray = []
    placemarker = 0
    averageTimeSpent = []
    ommitedDevices = 0

    #for node in nodes:

    listTracker = []
    for area in areas:
        count = 0
        aliveByArea = 0
        areaArray.append(area[0])
        areaDetectionArray.append(0)
        areaDetectionArrayALT.append(0)
        averageTimeSpent.append(0)
        nodeDetectionArray.append([0])
        nodeNameArray.append([])

        timebreakdown = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        datebreakdown = [0,0,0,0,0,0,0]

        for macAddress in macAddressPool:
            
            # get times for all mac addresses
            if macAddress[2] == area[0]:
                nodeNameArea = macAddress[3]
                aliveByArea = aliveByArea + macAddress[8]

                nodeNameExist = any(nodeNameArea in s for s in nodeNameArray)
                if not nodeNameExist:
                        loopCount = 0
                        for nodeName in nodeNameArray:
                            if nodeNameArray[loopCount] == []:
                                if not any(nodeNameArea in s for s in nodeNameArray):
                                    nodeNameArray[loopCount].append(nodeNameArea)
                                    listTracker.append(nodeNameArea)
                                    listTracker.append(loopCount)

                            loopCount = loopCount + 1
                        nodeNameArray.append([])
                        nodeDetectionArray.append([0])

                if nodeNameExist:
                    position = listTracker[listTracker.index(nodeNameArea) + 1]

                    nodeDetectionArray[position][0] = nodeDetectionArray[position][0] + 1

                timeSpentLive = macAddress[9]
                areaDetectionArray[placemarker] = areaDetectionArray[placemarker] + 1
                averageTimeSpent[placemarker] = averageTimeSpent[placemarker] + timeSpentLive

                detectionCountArea = int(macAddress[10])
                if detectionCountArea >= 100:
                    detectionCountArea = 0
                    ommitedDevices = ommitedDevices + 1
                areaDetectionArrayALT[placemarker] = areaDetectionArrayALT[placemarker] + detectionCountArea

                currentTime = macAddress[4]
                currentTime = int(currentTime[:2])
                timebreakdown[currentTime] = timebreakdown[currentTime] + 1
                if macAddress[7] != None:
                    previousTime = macAddress[7]
                    previousTime = int(previousTime[:2])
                    timebreakdown[previousTime] = timebreakdown[previousTime] + 1

                currentDate = macAddress[5]
                year, month, day = (int(x) for x in currentDate.split('-'))
                result = datetime.date(year, month, day)
                result = result.strftime("%A")
                if result == 'Monday':
                    datebreakdown[0] = datebreakdown[0] + 1
                elif result == 'Tuesday':
                    datebreakdown[1] = datebreakdown[1] + 1
                elif result == 'Wednesday':
                    datebreakdown[2] = datebreakdown[2] + 1
                elif result == 'Thursday':
                    datebreakdown[3] = datebreakdown[3] + 1
                elif result == 'Friday':
                    datebreakdown[4] = datebreakdown[4] + 1
                elif result == 'Saturday':
                    datebreakdown[5] = datebreakdown[5] + 1
                elif result == 'Sunday':
                    datebreakdown[6] = datebreakdown[6] + 1

                if (macAddress[6] != None) and (macAddress[6] != macAddress[5]):
                    currentDate = macAddress[5]
                    year, month, day = (int(x) for x in currentDate.split('-'))
                    result = datetime.date(year, month, day)
                    result = result.strftime("%A")
                    if result == 'Monday':
                        datebreakdown[0] = datebreakdown[0] + 1
                    elif result == 'Tuesday':
                        datebreakdown[1] = datebreakdown[1] + 1
                    elif result == 'Wednesday':
                        datebreakdown[2] = datebreakdown[2] + 1
                    elif result == 'Thursday':
                        datebreakdown[3] = datebreakdown[3] + 1
                    elif result == 'Friday':
                        datebreakdown[4] = datebreakdown[4] + 1
                    elif result == 'Saturday':
                        datebreakdown[5] = datebreakdown[5] + 1
                    elif result == 'Sunday':
                        datebreakdown[6] = datebreakdown[6] + 1
                count = count + 1

        if (count != 0) and (averageTimeSpent[placemarker] != 0):
            averageTimeSpent[placemarker] = averageTimeSpent[placemarker] / count
        placemarker = placemarker + 1


        timeArray.append(timebreakdown)
        dateArray.append(datebreakdown)
        liveArray.append(aliveByArea)
    print(areaDetectionArrayALT)
    areaNodes = []
    areaNodeArray = []
    areaNodeDet = []
    areaNodeDetArray = []

    for area in areas:
        for node in nodes:
            if area[0] == node[1]:
                areaNodes.append(node[0])
                position = listTracker[listTracker.index(node[0]) + 1]
                areaNodeDet.append(nodeDetectionArray[position][0])
        areaNodeArray.append(areaNodes)
        areaNodeDetArray.append(areaNodeDet)
        areaNodes = []
        areaNodeDet = []

    timebreakdown = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    datebreakdown = [0,0,0,0,0,0,0]

    for macAddress in macAddressPool:
        # get times for all mac addresses
        
        currentTime = macAddress[4]
        currentTime = int(currentTime[:2])
        timebreakdown[currentTime] = timebreakdown[currentTime] + 1
        if macAddress[7] != None:
            previousTime = macAddress[7]
            previousTime = int(previousTime[:2])
            timebreakdown[previousTime] = timebreakdown[previousTime] + 1  

        # get dates for all mac addresses
        currentDate = macAddress[5]
        year, month, day = (int(x) for x in currentDate.split('-'))
        result = datetime.date(year, month, day)
        result = result.strftime("%A")
        if result == 'Monday':
            datebreakdown[0] = datebreakdown[0] + 1
        elif result == 'Tuesday':
            datebreakdown[1] = datebreakdown[1] + 1
        elif result == 'Wednesday':
            datebreakdown[2] = datebreakdown[2] + 1
        elif result == 'Thursday':
            datebreakdown[3] = datebreakdown[3] + 1
        elif result == 'Friday':
            datebreakdown[4] = datebreakdown[4] + 1
        elif result == 'Saturday':
            datebreakdown[5] = datebreakdown[5] + 1
        elif result == 'Sunday':
            datebreakdown[6] = datebreakdown[6] + 1

        if (macAddress[6] != None) and (macAddress[6] != macAddress[5]):
            currentDate = macAddress[5]
            year, month, day = (int(x) for x in currentDate.split('-'))
            result = datetime.date(year, month, day)
            result = result.strftime("%A")
            if result == 'Monday':
                datebreakdown[0] = datebreakdown[0] + 1
            elif result == 'Tuesday':
                datebreakdown[1] = datebreakdown[1] + 1
            elif result == 'Wednesday':
                datebreakdown[2] = datebreakdown[2] + 1
            elif result == 'Thursday':
                datebreakdown[3] = datebreakdown[3] + 1
            elif result == 'Friday':
                datebreakdown[4] = datebreakdown[4] + 1
            elif result == 'Saturday':
                datebreakdown[5] = datebreakdown[5] + 1
            elif result == 'Sunday':
                datebreakdown[6] = datebreakdown[6] + 1


    #rows = db.execute(
    #    'SELECT macAddress FROM macAddressPool'
    #).fetchall()
    #enabled = False
    #if enabled:
    #    for row in rows:
    #        randomTime = random.randrange(5, 20, 5)
    #        db.execute(
    #               'UPDATE macAddressPool SET timeSpentLive=? WHERE macAddress=?',
    #                [randomTime, row[0]])
    db.commit()
    return render_template('main/index.html', timebreakdown=timebreakdown, datebreakdown=datebreakdown, areas=areas, timeArray=timeArray, dateArray=dateArray, areaArray=areaArray, areaDetectionArray=areaDetectionArray, averageTimeSpent=averageTimeSpent, areaNodeArray=areaNodeArray, areaNodeDetArray=areaNodeDetArray, areaDetectionArrayALT=areaDetectionArrayALT, ommitedDevices=ommitedDevices, liveArray=liveArray)

@bp.route('/maclist')
def mac_list():
    db = get_db()
    macAddressPool = db.execute(
        'SELECT macAddress, deviceType, areaName, nodeName, lastDetectTime, lastDetectDate, previousAliveDate, lastAliveTime, live, timeSpentLive, detectionCount, previousNode, previousArea, detectedNetwork FROM macAddressPool'
    ).fetchall()
    return render_template('main/maclist.html', macAddressPool=macAddressPool)

@bp.route('/areaconfig', methods=('GET', 'POST'))
@login_required
def area_config():
    return render_template('main/areaconfig.html')

@bp.route('/createarea', methods=('GET', 'POST'))
@login_required
def area_create():
    if request.method == 'POST':
        areaName = request.form['areaName']
        nodeList = request.form['nodelist']
        error = None
        nodeList = nodeList.split(',')

        if not areaName:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT areaName FROM areas WHERE areaName = ?", (areaName,))
            areaExist=cursor.fetchone()

            if nodeList != ['']:
                for node in nodeList:
                    cursor.execute("SELECT nodeName FROM nodes WHERE nodeName = ?", (node,))
                    nodeExist=cursor.fetchone()
                    if nodeExist is None:
                        flash(node + ' does not exist!')
                        return render_template('main/createarea.html')

            if areaExist is None:
                db.execute(
                    'INSERT INTO areas (areaName)'
                    ' VALUES (?)',
                    (areaName,)
                )
                
                for node in nodeList:
                    db.execute(
                        'UPDATE nodes SET areaName=? WHERE nodeName=?',
                         [areaName, node])
                    db.execute(
                        'UPDATE macAddressPool SET areaName=? WHERE nodeName=?',
                         [areaName, node])
                db.commit()
                return render_template('main/areaconfig.html')
            else:
                flash('Area already exists!')

    return render_template('main/createarea.html')

@bp.route('/selectarea', methods=('GET', 'POST'))
@login_required
def select_area():
    db = get_db()
    areas = db.execute(
        'SELECT areaName FROM areas'
    ).fetchall()

    if request.method == 'POST':
        if request.form['delete'] == "Delete":
            areaName = request.form['areaName']
            areaNameDefault = 'Default'

            nodeList = db.execute(
                'SELECT nodeName FROM nodes WHERE areaName=?',
                [areaName,]).fetchall()
            
            db.execute(
                'DELETE FROM areas WHERE areaName=?',
                 [areaName])

            for node in nodeList:
                    db.execute(
                        'UPDATE nodes SET areaName=? WHERE nodeName=?',
                         [areaNameDefault, node[0]])
                    db.execute(
                        'UPDATE macAddressPool SET areaName=? WHERE nodeName=?',
                         [areaNameDefault, node[0]])
            db.commit()
            return render_template('main/areaconfig.html', areas=areas)

    return render_template('main/selectarea.html', areas=areas)

@bp.route('/registernode', methods=('GET', 'POST'))
@login_required
def node_register():
    if request.method == 'POST':
        name = request.form['name']
        nodeip = request.form['nodeip']
        areaname = request.form['areaname']
        error = None

        if not name:
            error = 'Name is required.'

        if not nodeip:
            error = 'IP address is required'

        if not areaname:
            areaname = 'Default'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT nodeIP FROM nodes WHERE nodeIP = ?", (nodeip,))
            ipExist=cursor.fetchone()

            cursor.execute("SELECT areaName FROM areas WHERE areaName = ?", (areaname,))
            areaExist=cursor.fetchone()

            if ipExist is None:

                if areaExist is not None:
                    db.execute(
                        'INSERT INTO nodes (nodeIP, nodeName, areaName)'
                        ' VALUES (?,?,?)',
                        (nodeip, name, areaname)
                    )
                    db.commit()
                    return render_template('main/nodeconfig.html')

                else:
                    flash('Area does not exist!')
            else:
                flash('IP address already taken!')

    return render_template('main/registernode.html')

@bp.route('/nodeconfig', methods=('GET', 'POST'))
@login_required
def node_config():
    return render_template('main/nodeconfig.html')

@bp.route('/selectnode', methods=('GET', 'POST'))
@login_required
def select_node():
    db = get_db()
    nodes = db.execute(
        'SELECT nodeIP, nodeName, areaName FROM nodes'
    ).fetchall()
    return render_template('main/selectnode.html', nodes=nodes)
