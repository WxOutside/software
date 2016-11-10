#!/usr/bin/env python3
 
import json
import os
import RPi.GPIO as GPIO
import socket
import sys
import time

from aosong import am2315

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl
from functions import convert_to_bool, run_proc, date_time, update_last_record

# First, check if the user wants any temperature or humidity measurements:
host_name=socket.gethostname()

sensor = am2315.Sensor()
time.sleep(2.0)
sensor = am2315.Sensor()
humidity=sensor.humidity()
temperature=sensor.celsius()

date,hour,hour_readable,minutes=date_time()

# -99 etc is what happens if the sensor is not plugged in
if temperature!=-99.9 and humidity!=-999:
    
    print ("Temperature: " + str(temperature))
    print ("Humidity: " + str(humidity))
    
    doc_name=host_name + '_' + date + ':' + hour
    
    full_time=hour + ':' + minutes
    
    print ('Time:', hour+'00')
    
    #if hour>12:
    #    hour_readable=str(hour-12) + 'pm'
    #else:
    #    hour_readable=str(hour) + 'am'
    
    output=run_proc('GET', couchdb_baseurl + '/telemetry/' + doc_name)

    #Check to see if we already have a reading for this
    has_record=False
    try:
        if output['am2315_temperature']:
            has_record=True
            
        if output['am2315_humidity']:
            has_record=True
                
    except:
        pass
    
    if has_record:
        #print ('Status: Warning')
        print ('Code: 200')
        print ('Message: ' + hour_readable + " already has a record, we're not going to update it again")
        exit()
    
    json_items={}
    
    try:
        if output['_rev']:
            json_items=output
        
            #print ("We need to update rev_id " + json_items['_rev'])   
            
    except:
        # We need to add these values so that we can retreive them in views.
        # We only add these for new records because these values shouldn't change if the record is updated
        json_items['host_name']=host_name
        json_items['date']=date
        json_items['hour']=hour
        
    #Now load in our telemetry readings:
    json_items['am2315_temperature']=temperature
    json_items['am2315_humidity']=humidity
        
    # Now convert this data and save it
    json_string=json.dumps(json_items)   
    
    replication_output=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_name, json_string)
    #print ('Status: success')
    print ('Code: 100')
    print ('Message: ' + hour_readable + ' temperature and humidity reading taken at ' + full_time + ' (Temperature: ' + str(temperature) + '&deg;, Humidity: ' + str(humidity) + '%)')
    
    ###################################################
    # update the last_record entry:
    current_time=time.strftime("%Y-%m-%d %H:%M")
    
    json_items['am2315_last_updated']=current_time
    json_items['ignore']=True
    update_last_record(couchdb_baseurl, host_name, json_items)
else:
    #print ('Status: failure')
    print ('Code: 300')
    print ('Message: Errors found - check the cables!')
    