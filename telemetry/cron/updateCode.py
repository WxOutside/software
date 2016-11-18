#!/usr/bin/env python

import errno
import json
import ntpath
import os
import requests
import shutil
import stat
import StringIO
from subprocess import call
import sys
import time
import urllib2
import zipfile
from __builtin__ import True
 
sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl, wxoutside_sensor_name, wxoutside_sensor_password
from functions import run_proc

def get_latest(url):
    
    r = requests.get(url, stream=True)
    z = zipfile.ZipFile(StringIO.StringIO(r.content))
    z.extractall(path='/home/pi/telemetry/releases')
    
    return True

current_time=time.strftime("%Y-%m-%d %H:%M")
print ('Time:' + current_time)

# First, check for the correct version of the codebase we're supposed to be using
update_check='http://beta.wxoutside.tools/SelfUpdate/check?hostname=' + wxoutside_sensor_name + '&password=' + wxoutside_sensor_password

headers = { 'User-Agent' : 'Mozilla/5.0' }
req = urllib2.Request(update_check, None, headers)
update_url = urllib2.urlopen(req).read()

# Now check to see what version we currently have
file_name=ntpath.basename(update_url).strip('.zip')
existing_record=run_proc('GET', couchdb_baseurl + '/hardware/' + wxoutside_sensor_name)

try:
    if existing_record['_rev']:
        sensor_record=existing_record
except:
    del existing_record['error']
    del existing_record['reason']

    sensor_record={}
    
try:
    current_version=sensor_record['software_version']
except:
    current_version=''
    
#if current_version==file_name:
#    print ('Message: Software is already current - version ' + file_name)
#    exit()
    
# Go and get this update
get_latest(update_url)

# Now copy the various files and folders over to the new destination
source_files=['autorun', 'cron', 'functions.py', 'sensors']

base_path='/home/pi/telemetry/'
for source in source_files:
    full_path='/home/pi/telemetry/releases/software-' + file_name + '/telemetry/' + source
    destination=base_path+source
    
    # Delete the existing folder or file
    try:
        shutil.rmtree('/home/pi/telemetry/' + source)
    except:
        pass
    
    try:
        shutil.copytree(full_path, destination)
        
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(full_path, destination)
        else: raise
        
# import the crontab
call(['crontab ' + '/home/pi/telemetry/releases/software-' + file_name + '/telemetry/misc/crontab.master'], shell=True)

# Some tidy up activities:
# First - grant the right permissions to the agent:
weather_agent=base_path + 'sensors/weatherPiArduino/weatherPiArduino_agent.py'
st = os.stat(weather_agent)
os.chmod(weather_agent, st.st_mode | stat.S_IEXEC)
# Second - delete the release
shutil.rmtree(full_path)

# Now update the sensor records with this version
sensor_record['software_version']=file_name

json_string=json.dumps(sensor_record)   
result=run_proc('PUT', couchdb_baseurl + '/hardware/' + wxoutside_sensor_name, json_string)

# All done!
print ('Message: Software successfully updated to ' + file_name)
