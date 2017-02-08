#!/usr/bin/env python

import os
import subprocess
import sys
import time
	
sys.path.append(os.path.abspath('/home/pi/telemetry/'))

from functions import date_time

process_found=False
proc = subprocess.Popen(["ps ax | grep weatherPiArduino_agent"], shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)

temp_logfile='/home/pi/telemetry/logs/weatherPiArduino_controller.log'
for line in iter(proc.stdout.readline,''):
	if(line.find("/home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_agent.py")>-1):
		process_found=True
		
if process_found==True:
	date,hour,hour_readable,minutes=date_time()

	full_date=str(date) + ' ' + str(hour) + ':' + str(minutes)
	print ('Time: ' + full_date)
	print ('Code: 200')
	print ('Message: Script already running')
	exit()
	
os.system("/home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_agent.py")
