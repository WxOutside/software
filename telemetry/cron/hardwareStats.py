#!/usr/bin/env python

import json
import os
import socket
#import subprocess
import sys

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl
from functions import run_proc, getCPUtemperature, getCPUuse, getRAMinfo, getDiskSpace, date_time

host_name=socket.gethostname()

cpu_temp=getCPUtemperature()
cpu_usage=getCPUuse()
ram_total,ram_used,ram_free=getRAMinfo()
disk_total,disk_used,disk_remaining,disk_percent=getDiskSpace()

date,hour,hour_readable,minutes=date_time()

existing_record=run_proc('GET', couchdb_baseurl + '/hardware/' + host_name)
try:
    if existing_record['_rev']:
        sensor_record=existing_record
        
except:
    del existing_record['error']
    del existing_record['reason']
    sensor_record={}

sensor_record['cpu_temperature']=float(cpu_temp)
sensor_record['cpu_usage']=cpu_usage + '%'
sensor_record['ram_total']=str(round(float(ram_total)/1024,2)) + 'MB'
sensor_record['ram_used']=str(round(float(ram_used)/1024,2)) + 'MB'
sensor_record['ram_free']=str(round(float(ram_free)/1024,2)) + 'MB'
sensor_record['ram_percent']=str(round(round(float(ram_used)/1024,2) / round(float(ram_total)/1024,2)*100,2)) + '%' 
sensor_record['disk_total']=disk_total + 'B'
sensor_record['disk_used']=disk_used + 'B'
sensor_record['disk_remaining']=disk_remaining + 'B'
sensor_record['disk_percent']=disk_percent

sensor_record['host_name']=host_name
sensor_record['date']=date
sensor_record['hour']=hour

json_string=json.dumps(sensor_record)

# Now convert this data and save it
json_string=json.dumps(sensor_record)   
    
result=run_proc('PUT', couchdb_baseurl + '/hardware/' + host_name, json_string)

print (result)
print ('done, hardware record updated!')