#!/usr/local/opt/python-3.5.1/bin/python3.5
# SDI-12 Sensor Data Logger Copyright Dr. John Liu 2016-02-09
import getopt
import serial.tools.list_ports
import serial
import time
#import datetime
#import re
import sys

from config import *
from functions import *

def main(argv):

    # First, find out if any parameters were passed
    new_address=''
    new_soil=''
    try:
        opts, args = getopt.getopt(argv,"a:s:",["new=", "soil="])
    except getopt.GetoptError:
        print ('aquaflex_logger.py -new <new_address>')
        sys.exit(2)
        
    for opt, arg in opts:
        if opt in ("-a", "--address"):
            new_address = bytes(arg, encoding='utf-8')
        elif opt in ("-s", "--soil"):
            new_soil=arg
            
    change_address=False
    if new_address!='':
        change_address=True
        
    change_soil=False
    if new_soil!='':
        change_soil=True
        
    # Initialise the device
    device=serial.Serial("/dev/ttyUSB0",baudrate=9600,timeout=10)
    
    time.sleep(2.5) # delay for arduino bootloader and the 1 second delay of the adapter.
    
    # Now get the address from the serial device we've connected to.
    # We'll reuse this for every message
    address=device_address(device)
    
    if address==b'':
        print ('No valid address could be found, is the sensor plugged in (also check the battery)?')
        exit()
        
    if change_address:
        changed=change_device_address(device, address, new_address)
       
        if changed==new_address:
            print ('Device address changed successfully')
        else:
            print ('Device address could not be changed')
            
        exit()
    
    if change_soil:
        changed=change_soil_type(device, address, new_soil)
        
        if changed==new_soil:
            print ('Soil type changed successfully')
        else:
            print ('Soil type could not be changed')
            
        exit()
    
    # Not really sure if this might be a problem, but we'll check that the details match:
    if device_acknowledgement(device, address)!=address:
        print ('The device address does not match the acknowledged address, exiting')
        exit()
        
    # Get the identification value for this device.
    sdi_version,vendor,model,version=device_identification(device, address)
    
    # the only thing we really care about is that the sdi version and the sensor version match what we expect
    if sdi_version!=config_sdi_version:
        print ('The sensor is using the wrong SDI standard (',sdi_version,')  - we are expecting SDI-12 version 1.3')
        exit()
   
    if version not in config_versions:
        print ('The sensor is the wrong version (',version,') - we are expecting version 130')
        exit()
        
    # Check that the soil type matches what we're expecting
    soil_type=query_soil_type(device, address)
    
    if soil_type!=config_soil_type:
        print ('The sensor is configured for the wrong soil type (',soil_type,') - we are expecting "clay"')
        exit()
        
    delay, data_items=measurement_request(device, address)
    
    # For some reason, if the delay>0, we have to do another read before we can make a data request
    if delay>0:
        device.readline()
    time.sleep(delay)
    
    soil_moisture, soil_temperature, battery_voltage, raw1, raw2=get_data(device, address)
    
    # Check that the soil mosture reading doesn't contain an error code, one of the following:
    # 0.01: Damaged
    # 0.02: Low power. The voltage too low to take a reading)
    # 0.03: Corrupt configuration. This has never been reported. It means that the configuration has failed its CRC checks and the calibration cannot be relied on.
    error_code=soil_moisture.split('.')[1]
    if error_code=='-01':
        error_message='Sensor is damaged or sitting in the open air.'
    elif error_code=='-02':
        error_message='Low power. The voltage is too low to take a reading.'
    elif error_code=='-03':
        error_message='Corrupt configuration. The configuration has failed its CRC checks and the calibration cannot be relied on.'
    else:
        error_message=False
        
    if error_message!=False:
        print (error_message)
        #exit();
    
    print('soil moisture:', soil_moisture, 'soil temperature:', soil_temperature, 'voltage:', battery_voltage)
    print('raw1:', raw1, 'raw2:', raw2)
        
    vmc=0
    lmc=raw2-raw1
    corner1=raw1
    corner2=corner1*corner1
    corner3=corner2*corner1
    corner4=corner3*corner1
    
    if soil_type=='clay':
        vmc = 100.0 * (1.00 - 0.32 * (lmc - 0.36)) * (1.7875 - 0.3674 * corner1 + 0.01945 * corner2 + 0.0000512 * corner3 - 0.00001039 * corner4);
    elif soil_type=='sand':
        vmc = 100.0 * (1.00 - 0.30 * (lmc - 0.30)) * (-2.282 + 0.6685 * corner1 - 0.07623 * corner2 + 0.0038130 * corner3 - 0.00006361 * corner4);
        
    if vmc<0:
        vmc=0
        
    vmc=round(vmc, 2)
    
    print ('moisture: ',vmc)
    device.close()

if __name__ == "__main__":
   main(sys.argv[1:])
