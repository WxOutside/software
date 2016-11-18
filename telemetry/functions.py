#!/usr/bin/env python

import subprocess
import json
import os
import smtplib
import time

from config import couchdb_baseurl, wxoutside_email_server, wxoutside_email_port
from environment_config import wxoutside_sensor_email, wxoutside_sensor_password

def get_sensor_config_value(item):
    output=run_proc('GET', couchdb_baseurl + '/config/sensors')
    status=False
    try:
        status=convert_to_bool(output[item])
    except:
        pass
    
    return status

def convert_to_bool(val):
    "Take the provided value and see if it looks like 'true' or 'false'"
    if val=='true' or val=='True' or val==True:
        return True
    if val=='false' or val=='False' or val==False:
        return False
    
    
def run_proc(request_type, path, json_string=False):
    
    if request_type=='GET':
        proc=subprocess.Popen(['curl', '-X', 'GET', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            output=proc.stdout.read()
            output=json.loads(output)
        except:
            output=False
    
    else:
        proc=subprocess.Popen(['curl', '-X', 'PUT', path , '-d', json_string, '-H', 'Content-Type: application/json'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        try:
            output=proc.stdout.read()
            output=json.loads(output)
        except:
            output=False

    return output

# Return the core components of the current date and time
def date_time():
    date=time.strftime("%Y-%m-%d")
    hour=time.strftime('%H')
    hour2=time.strftime('%I%p').lstrip('0')
    minutes=time.strftime('%M')
    
    return date,hour,hour2,minutes

# Return CPU temperature as a character string                                     
def getCPUtemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    return(res.replace("temp=","").replace("'C\n",""))

# Return RAM information (unit=kb) in a list                                       
# Index 0: total RAM                                                               
# Index 1: used RAM                                                                 
# Index 2: free RAM                                                                 
def getRAMinfo():
    p = os.popen('free')
    i = 0
    while 1:
        i = i + 1
        line = p.readline()
        if i==2:
            return(line.split()[1:4])

# Return % of CPU used by user as a character string                               
#def getCPUuse():
#    return(str(os.popen("top -n1 | awk '/Cpu\(s\):/ {print $2}'").readline().strip(\
#)))
    
def getCPUuse():
    return(str(os.popen("top -d 0.5 -b -n2 | grep \"Cpu(s)\"|tail -n 1 | awk '{print $2 + $4}'").readline()).strip('\n'))

# Return information about disk space as a list (unit included)                     
# Index 0: total disk space                                                         
# Index 1: used disk space                                                         
# Index 2: remaining disk space                                                     
# Index 3: percentage of disk used                                                 
def getDiskSpace():
    p = os.popen("df -h /")
    i = 0
    while 1:
        i = i +1
        line = p.readline()
        if i==2:
            return(line.split()[1:5])

# Given a host name and some record items, update the last_record value
def update_last_record(base_url, host_name, new_json_items):
    
    new_json_items['ignore']=True
    
    try:
        if new_json_items['_rev']:
            del new_json_items['_rev']
            
    except:
        pass
        
    doc_name=host_name + '_last_record'
    output=run_proc('GET', base_url + '/telemetry/' + doc_name)
        
    last_record_json_items={}
    
    try:
        if output['_rev']:
            last_record_json_items=output
    
            #print ("We need to update rev_id " + last_record_json_items['_rev'])   
            
    except:
        pass
        
    # Merge the two dictionaries
    z = last_record_json_items.copy()
    z.update(new_json_items)
    
    # Now convert this data and save it
    json_string=json.dumps(z)   
    
    replication_output=run_proc('PUT', base_url + '/telemetry/' + doc_name, json_string)
    #print ('Record written to ' + doc_name)
    #print (replication_output)
    
    return replication_output
    
# Generic 'send email' function
def send_email(subject, text):
    server = smtplib.SMTP(wxoutside_email_server, wxoutside_email_port)
    server.starttls()
    server.login(wxoutside_sensor_email, wxoutside_sensor_password)
     
    message = 'Subject: %s\n\n%s' % (subject, text)
    
    from_address=wxoutside_sensor_email
    to_address=wxoutside_sensor_email
    server.sendmail(from_address, to_address, message)
    server.quit()
    
    return True
