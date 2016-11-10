#!/usr/bin/env python

import json
import os
import socket
import sys
import time

import RPi.GPIO as GPIO
from __builtin__ import True

sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/RTC_SDL_DS3231'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/Adafruit_Python_GPIO'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/SDL_Pi_Weather_80422'))
sys.path.append(os.path.abspath('/home/pi/telemetry/sensors/weatherPiArduino/SDL_Pi_Weather_80422/Adafruit_ADS1x15'))

import SDL_DS3231
import SDL_Pi_Weather_80422 as SDL_Pi_Weather_80422

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

weatherStation=create_connection()

#weatherStation.setWindMode(SDL_MODE_SAMPLE, 5.0)
weatherStation.setWindMode(SDL_MODE_DELAY, 5.0)

# Main Program
host_name=socket.gethostname()
wind_speeds=[]
max_wind_gust=0
total_rain = 0

first=True
continue_loop=True
while continue_loop:

	current_wind_speed = weatherStation.current_wind_speed() * 1.852
	current_wind_gust = weatherStation.get_wind_gust() * 1.852
	total_rain = total_rain + weatherStation.get_current_rain_total()
	current_wind_direction=weatherStation.current_wind_direction()
	
	# If the wind speed is zero, then the wind direction if false (ie, no direction)
	if current_wind_speed==0:
		current_wind_direction=False
		
	if first==False:
			
		wind_speeds.append(current_wind_speed)
		#print ('current wind gust: ', current_wind_gust)
		#print ('max wind gust: ', max_wind_gust)
		if current_wind_gust>=max_wind_gust:
			#print ('setting new wind details')
			max_wind_gust=current_wind_gust
			max_wind_gust_direction=current_wind_direction
			#print ('max wind gust direction: ', max_wind_gust_direction)
			#print ("")
			
		avg_wind_speed=sum(wind_speeds) / float(len(wind_speeds))
		#print ('average wind speed: ', avg_wind_speed)
		#print ('max wind gust:', max_wind_gust)
		#print ('max wind gust direction:', str(max_wind_gust_direction))
		#print ('current wind direction:', str(current_wind_direction))
		#print ('total rain: ' , total_rain)
		
		current_minute=time.strftime("%M")
		current_time=time.strftime("%Y-%m-%d %H:%M:%S")
		
		if current_minute=='00':
			#print ('updating official record')
			
			date,hour=date_time()
			doc_name=host_name + '_' + date + ':' + hour
			output=run_proc('GET', couchdb_baseurl + '/telemetry/' + doc_name)
			
			json_items={}
			try:
				if output['_rev']:
					json_items=output
									
			except:
				# We need to add these values so that we can retreive them in views.
				# We only add these for new records because these values shouldn't change if the record is updated
				json_items['host_name']=host_name
				json_items['date']=date
				json_items['hour']=hour
				
			#Now load in our telemetry readings:
			json_items['anemometer_wind_speed']=avg_wind_speed
			json_items['anemometer_wind_gust']=max_wind_gust
			json_items['anemometer_wind_direction']=max_wind_gust_direction
			
			json_items['anemometer_precipitation']=total_rain
		
			# Now convert this data and save it
			json_string=json.dumps(json_items)   
			replication_output=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_name, json_string)
			
			###################################################
			# update the last_record entry:
			current_time=time.strftime("%Y-%m-%d %H:%M")
			json_items['anemometer_last_updated']=current_time
			json_items['ignore']=True
			update_last_record(couchdb_baseurl, host_name, json_items)
			
			print ('Time: ' + current_time)
			print ('Code: 100')
			print ('Rain: ', total_rain)
			print ('Average wind: ', avg_wind_speed)
			print ('Max wind gust: ', max_wind_gust)
			print ('Max wind gust direction: ', max_wind_gust_direction)
			print ('Message: ' + hour2 + ' record -  Rain: ' + str(total_rain) + ', average wind: ' + str(avg_wind_speed) + ', max wind gust: ' + str(max_wind_gust) + ', max wind gust direction: ' + str(max_wind_gust_direction))
			
			wind_speeds=[]
			max_wind_gust=0
			total_rain = 0
					
		time.sleep(10.0)
		
	else:
		first=False
		time.sleep(10.0)
		max_wind_gust=0
		total_rain=0
		