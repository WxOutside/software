#!/usr/bin/env python

import json
import os
import smtplib
import sys
import time

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import couchdb_baseurl, wxoutside_email_server, wxoutside_email_port, wxoutside_sensor_email, wxoutside_sensor_password
from functions import run_proc, convert_to_bool

version='v1'

unsent_records=run_proc('GET', couchdb_baseurl + '/telemetry/_design/records/_view/unsent')

for row in unsent_records['rows']:
    
    values=row['value']
    
    body=''
    header=''
    
    #print ('values:')
    #print (values)
    valid=True
    try:
        date=values['date']
        hour=values['hour']
        host_name=values['host_name']
        doc_name=values['_id']
    except:
        valid=False
        
    try:
        email_sent=convert_to_bool(values['email_sent'])
    except:
        email_sent=False
        
    if valid==True and email_sent==False:
        json_items=values
        
        #header=str(version) + '/' + str(date) + '/' + str(hour) + '/' + str(host_name) + "\n"
        header=str(version) + '/' + host_name + '/telemetry/' + str(date) + ' ' + str(hour) + ':00' + "\n"
        
        for value_item in values:
            if value_item!='_rev' and value_item!='date' and value_item!='hour' and value_item!='host_name' and value_item!='email_sent':
                
                if value_item=='_id':
                    value_item_display='DocumentID'
                else:
                    value_item_display=value_item
                    
                print ('value item:', values[value_item])
                body=body + value_item_display + ':' + str(values[value_item]) + "\n"
        
        print (header)
        print ('body:', body)
                
        server=smtplib.SMTP(wxoutside_email_server, wxoutside_email_port)
        server.starttls()
        server.login(wxoutside_sensor_email, wxoutside_sensor_password)
         
        text = str(header) + str(body)
        message = 'Subject: %s\n\n%s' % ('Telemetry data', text)
    
        from_address=wxoutside_sensor_email
        to_address=wxoutside_sensor_email
        server.sendmail(from_address, to_address, message)
        server.quit()
        
        json_string=json.dumps(json_items)
        
        print ('json string:')
        print(json_string)
        
        updated_record=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_name, json_string)
        
        print ('sent... sleeping for 5 seconds before the next one')
        
        time.sleep(5.0)
                
            #exit() 
    #except:
    #    print ("bad data, can't send email for ", values)
    #    exit()

print ('all done!')
