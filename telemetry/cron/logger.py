#!/usr/bin/env python

import datetime
import glob
import json
import os
import smtplib
import socket
import sys

def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import wxoutside_email_server, wxoutside_email_port, wxoutside_sensor_email, wxoutside_sensor_password

version='v1'
header=''
body=''

host_name=socket.gethostname()

# -rw-r--r-- 1 pi pi    563 Aug  5 21:01 am2315.log
# -rw-r--r-- 1 pi pi    233 Aug  5 20:50 checkEmail.log
# -rw-r--r-- 1 pi pi    567 Aug  5 03:30 compaction.log
# -rw-r--r-- 1 pi pi    133 Aug  5 21:04 hardwareStats.log
# -rw-r--r-- 1 pi pi    161 Aug  5 20:51 sendHardwareStats.log
# -rw-r--r-- 1 pi pi  33702 Aug  5 20:55 sendTelemetry.log
# -rw-r--r-- 1 pi pi    282 Aug  5 21:02 soil.log
# -rw-r--r-- 1 pi pi     32 Jul 31 10:17 uptimeLogger.log
# -rw-r--r-- 1 pi pi 162918 Aug  5 21:03 weatherPiArduino_controller.log

logs=['am2315', 'aquaflex', 'compaction', 'rebootLogger', 'weatherPiArduino_controller']

for log_name in logs:
    filepath='/home/pi/telemetry/logs/' + str(log_name) + '.*.log'
    
    txt = glob.glob(filepath)
    for textfile in txt:
        with open(textfile, 'r') as content_file:
            
            print ('opening ' + textfile)
            
            body = content_file.read()
        
            modified_date=modification_date(textfile)
            
            header=str(version) + '/' + str(log_name) + '/' + str(modified_date) + '/' + str(host_name) + "\n"
            
            server = smtplib.SMTP(wxoutside_email_server, wxoutside_email_port)
            server.starttls()
            server.login(wxoutside_sensor_email, wxoutside_sensor_password)
             
            text = str(header) + str(body)
            message = 'Subject: %s\n\n%s' % ('Log file: ' + log_name, text)
            
            from_address=wxoutside_sensor_email
            to_address=wxoutside_sensor_email
            server.sendmail(from_address, to_address, message)
            server.quit()
        
            # remove this file    
            os.remove(textfile)
            
            print ('sent ' + log_name + ' details!')

print ('all done!')