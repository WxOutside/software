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

import json
import os
import socket
import sys
import time

import RPi.GPIO as GPIO
from __builtin__ import True

sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/RTC_SDL_DS3231'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/Adafruit_Python_BMP'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/Adafruit_Python_GPIO'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/SDL_Pi_Weather_80422'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/SDL_Pi_Weather_80422/Adafruit_ADS1x15'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/SDL_Pi_FRAM'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/RaspberryPi-AS3935/RPi_AS3935'))

import SDL_DS3231
import Adafruit_BMP.BMP085 as BMP180
import SDL_Pi_Weather_80422 as SDL_Pi_Weather_80422

import SDL_Pi_FRAM
from RPi_AS3935 import RPi_AS3935

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl
from functions import run_proc, date_time, get_sensor_config_value, update_last_record

def create_connection():
	try:
		result = SDL_Pi_Weather_80422.SDL_Pi_Weather_80422(anenometerPin, rainPin, 0,0, SDL_MODE_I2C_ADS1015)
	except:
		GPIO.cleanup()
		
		result=False
		
	return result

# Find out if we're configered to get wind and rain readings:
#get_wind=get_sensor_config_value('anemometer_wind')
#get_rain=get_sensor_config_value('anemometer_rain')

#print ('get wind:', get_wind)           
#print ('get rain:', get_rain)

#if get_wind==False and get_rain==False:
#	print ('This sensor is not configured to measure wind or rain, exiting...')
#	exit()

################
anenometerPin = 23
rainPin = 24

# constants
SDL_MODE_INTERNAL_AD = 0
SDL_MODE_I2C_ADS1015 = 1

#sample mode means return immediately.  THe wind speed is averaged at sampleTime or when you ask, whichever is longer
SDL_MODE_SAMPLE = 0
#Delay mode means to wait for sampleTime and the average after that time.
SDL_MODE_DELAY = 1

logfile='/home/pi/telemetry/logs/weatherPiArduino_agent.log'

print ""
print "WeatherPiArduino Demo / Test Version 1.0 - SwitchDoc Labs"
print ""
print ""
print "Program Started at:"+ time.strftime("%Y-%m-%d %H:%M:%S")
print ""

weatherStation=create_connection()
weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
#weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)

# Main Program
host_name=socket.gethostname()
wind_speeds=[]
max_wind_gust=0
total_rain = 0

first=True
continue_loop=True
while continue_loop:

	print "---------------------------------------- "
	print "----------------- "
	print " WeatherRack Weather Sensors" 
	print "----------------- "
	current_wind_speed = weatherStation.current_wind_speed() * 1.852
	current_wind_gust = weatherStation.get_wind_gust() * 1.852
	total_rain = total_rain + weatherStation.get_current_rain_total()
	current_wind_direction=weatherStation.current_wind_direction()
	
	# If the wind speed is zero, then the wind direction if false (ie, no direction)
	if current_wind_speed==0:
		current_wind_direction=False
		
	if first==False:
			
		wind_speeds.append(current_wind_speed)
		print ('current wind gust: ', current_wind_gust)
		print ('max wind gust: ', max_wind_gust)
		if current_wind_gust>=max_wind_gust:
			print ('setting new wind details')
			max_wind_gust=current_wind_gust
			max_wind_gust_direction=current_wind_direction
			print ('max wind gust direction: ', max_wind_gust_direction)
			print ("")
			
		avg_wind_speed=sum(wind_speeds) / float(len(wind_speeds))
		print ('average wind speed: ', avg_wind_speed)
		print ('max wind gust:', max_wind_gust)
		print ('max wind gust direction:', str(max_wind_gust_direction))
		print ('current wind direction:', str(current_wind_direction))
		print ('total rain: ' , total_rain)
		
		current_minute=time.strftime("%M")
		current_time=time.strftime("%Y-%m-%d %H:%M:%S")
		
		if current_minute=='00':
			print ('updating official record')
			
			date,hour=date_time()
			doc_name=host_name + '_' + date + ':' + hour
			output=run_proc('GET', couchdb_baseurl + '/telemetry/' + doc_name)
			
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
			#if get_wind:
			print ('updating wind')
			json_items['anemometer_wind_speed']=avg_wind_speed
			json_items['anemometer_wind_gust']=current_wind_gust
			json_items['anemometer_wind_direction']=max_wind_gust_direction
			
			#if get_rain:
			print ('updating rain')
			json_items['anemometer_precipitation']=total_rain
		
			# Now convert this data and save it
			json_string=json.dumps(json_items)   
			
			print ('total rain is ' + str(total_rain));
			print (json_string)
			
			replication_output=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_name, json_string)
			print ('Record written to ' + doc_name)
			print (replication_output)
			
			###################################################
			# update the last_record entry:
			current_time=time.strftime("%Y-%m-%d %H:%M:%S")
			json_items['anemometer_last_updated']=current_time
			json_items['ignore']=True
			update_last_record(couchdb_baseurl, host_name, json_items)
			wind_speeds=[]
			max_wind_gust=0
			total_rain = 0
					
		time.sleep(10.0)
		
	else:
		print ('skipping first attempt')
		first=False
		time.sleep(10.0)
		max_wind_gust=0
		total_rain=0
		