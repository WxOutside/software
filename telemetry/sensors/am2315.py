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

output=run_proc('GET', couchdb_baseurl + '/config/sensors')
    
#get_humidity=convert_to_bool(output['am2315_humidity'])
#get_temperature=convert_to_bool(output['am2315_temperature'])

#print ('get humidity:', get_humidity)           
#print ('get temperature:', get_temperature)

#if get_humidity==False and get_temperature==False:
#    print ('This sensor is not configured to measure humidity and temperature, exiting...')
#    exit()
    
sensor = am2315.Sensor()
time.sleep(2.0)
humidity=sensor.humidity()
temperature=sensor.celsius()

date,hour=date_time()

# -99 etc is what happens if the sensor is not plugged in
if temperature!=-99.9 and humidity!=-999:
    
    print ("Temperature: " + str(temperature) + " humidity: " + str(humidity))

    doc_name=host_name + '_' + date + ':' + hour
    
    output=run_proc('GET', couchdb_baseurl + '/telemetry/' + doc_name)

    #Check to see if we already have a reading for this
    has_record=False
    try:
        #if get_temperature:
        if output['am2315_temperature']:
            has_record=True
            
        #if get_humidity:
        if output['am2315_humidity']:
            has_record=True
                
    except:
        print ("No record for this hour, let's create one!")
    
    if has_record:
        print ("This hour already has a record, we're not going to update it again")
        exit()
    
    #print (output)
    
    json_items={}
    
    try:
        if output['_rev']:
            json_items=output
        
            print ("We need to update rev_id " + json_items['_rev'])   
            
    except:
        print ("No entry for this hour, not updating a revision")
        # We need to add these values so that we can retreive them in views.
        # We only add these for new records because these values shouldn't change if the record is updated
        json_items['host_name']=host_name
        json_items['date']=date
        json_items['hour']=hour
        
    #Now load in our telemetry readings:
    #if get_temperature:
    json_items['am2315_temperature']=temperature
        
    #if get_humidity:
    json_items['am2315_humidity']=humidity
        
    # Now convert this data and save it
    json_string=json.dumps(json_items)   
    
    replication_output=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_name, json_string)
    print ('Record written to ' + doc_name)
    #print (replication_output)
    
    ###################################################
    # update the last_record entry:
    current_time=time.strftime("%Y-%m-%d %H:%M:%S")
    json_items['am2315_last_updated']=current_time
    json_items['ignore']=True
    update_last_record(couchdb_baseurl, host_name, json_items)
else:
    print ('Errors found - check the cables!')
    