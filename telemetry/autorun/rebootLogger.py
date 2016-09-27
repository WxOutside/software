#!/usr/bin/env python

import os
import sys
import time

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from functions import send_email
from config import wxoutside_sensor_name

logfile='/home/pi/telemetry/logs/uptimeLogger.log'

date=time.strftime("%Y-%m-%d %H:%M:%S")

target = open(logfile, 'a')

target.write('rebooted at ' + str(date))
target.write("\n")
target.close()

header='v1/' + str(wxoutside_sensor_name) + "/system event/" + str(date) + "\n"
body="system restarted\n"
body=body + str(date) + "\n";
body=body + 'System restarted at ' + str(date) + "\n"

send_email('System event response', header + body)