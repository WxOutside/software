#!/usr/bin/env python
#
# WeatherPiArduino Test File
# Version 1.1 February 12, 2015
#
# SwitchDoc Labs
# www.switchdoc.com
#
#

# imports

# pi@bear1 / $ ps ax | grep weatherPiArduino

#from datetime import datetime
import os
#import socket
import subprocess
import sys
import time
	
sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from functions import update_log

process_found=False
proc = subprocess.Popen(["ps ax | grep weatherPiArduino_agent"], shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)

temp_logfile='/home/pi/telemetry/logs/weatherPiArduino_controller.log'
update_log(temp_logfile, 'trying to start at ' + str(time.strftime("%Y-%m-%d %H:%M:%S")))
for line in iter(proc.stdout.readline,''):
	print (line)
	
	update_log(temp_logfile, line)
	if(line.find("/home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_agent.py")>-1):
		process_found=True
		update_log(temp_logfile, 'process found!')

if process_found==True:
	print ('Script already running')
	update_log(temp_logfile, 'script already running, exiting!')
	exit()
	
update_log(temp_logfile, 'script good to go!')

os.system("/home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_agent.py")
	

