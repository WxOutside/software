#!/usr/bin/env python

#import json
import os
import smtplib
import socket
import sys
#import time

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl, wxoutside_email_server, wxoutside_email_port, wxoutside_sensor_email, wxoutside_sensor_password, wxoutside_sensor_name
from functions import run_proc

host_name=socket.gethostname()

version='v1'

hardware_record=run_proc('GET', couchdb_baseurl + '/hardware/' + host_name)

body=''
header=''

date=hardware_record['date']
hour=hardware_record['hour']
host_name=hardware_record['host_name']
doc_name=hardware_record['_id']
    
json_items=hardware_record

header=str(version) + '/' + wxoutside_sensor_name + '/hardware data/' + str(date) + ' ' + hour + ':00' + "\n"
        
for value_item in hardware_record:
    if value_item!='_rev' and value_item!='date' and value_item!='hour' and value_item!='host_name':
        
        if value_item=='_id':
            value_item_display='DocumentID'
        else:
            value_item_display=value_item
            
        print ('value item:', hardware_record[value_item])
        body=body + value_item_display + ':' + str(hardware_record[value_item]) + "\n"
        
print (header)
print ('body:', body)

server = smtplib.SMTP(wxoutside_email_server, wxoutside_email_port)
server.starttls()
server.login(wxoutside_sensor_email, wxoutside_sensor_password)
 
text = str(header) + str(body)
message = 'Subject: %s\n\n%s' % ('Hardware data', text)

from_address=wxoutside_sensor_email
to_address=wxoutside_sensor_email
server.sendmail(from_address, to_address, message)
server.quit()

print ('sent hardware details!')
