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
from config import wxoutside_email_server, wxoutside_email_port
from environment_config import wxoutside_sensor_email, wxoutside_sensor_password

version='v1'
header=''
body=''

host_name=socket.gethostname()

logs=['am2315', 'aquaflex', 'compaction', 'rebootLogger', 'updateCode', 'weatherPiArduino_controller']

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