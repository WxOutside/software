#!/usr/bin/env python

from email import parser
import json
import os
import poplib
import sys

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from config import wxoutside_email_server, wxoutside_email_port, couchdb_baseurl
from environment_config import wxoutside_sensor_name, wxoutside_sensor_email, wxoutside_sensor_password
from functions import run_proc

from sensors.aquaflex import aquaflex_functions

from datetime import datetime
from dateutil.relativedelta import relativedelta

pop_conn = poplib.POP3_SSL(wxoutside_email_server)
pop_conn.user(wxoutside_sensor_email)
pop_conn.pass_(wxoutside_sensor_password)
#Get messages from server:
messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
# Concat message pieces:
messages = ["\n".join(mssg[1]) for mssg in messages]
#Parse message intom an email object:
messages = [parser.Parser().parsestr(mssg) for mssg in messages]
                            
count=0;
for message in messages:
    count=count+1;
    
    target_subject='Receipt for ' + wxoutside_sensor_name
    subject=message['subject'][0:len(target_subject)];
    if subject==target_subject:
        for part in message.walk():
            #print (part);
            if part.get_content_type():
                body = part.get_payload(decode=True)
                
                # Assume that the only line is the document ID:
                if body is not None:
                    body=body.replace("\n\n", "\n")
                    lines=body.split("\n")
                    if lines[0].split('/')[0]=='v1':
                        print ('document id: ', lines[1])
                        document_id=lines[1]
                        
                        output=run_proc('GET', couchdb_baseurl + '/telemetry/' + document_id)
                        
                        output['email_sent']=True
                        
                        #Mark this record as being deleted    
                        output['_deleted']=True
                        
                        # Now convert this data and save it
                        json_string=json.dumps(output)   
                            
                        updated_doc=run_proc('PUT', couchdb_baseurl + '/telemetry/' + document_id, json_string)
                        print (updated_doc)
                        
                        print ('deleting email...');
                        pop_conn.dele(count);
    
    # Now lookfor admin messags for this sensor
    target_subject='Admin command for ' + wxoutside_sensor_name
    subject=message['subject'][0:len(target_subject)];
    
    if subject==target_subject:
        print ('found a match: ' + subject + ' = ' + target_subject)
        for part in message.walk():
            if part.get_content_type():
                body = part.get_payload(decode=True)
                
                # Assume that the only line is the document ID:
                if body is not None:
                    body=body.replace("\n\n", "\n")
                    line_bits=body.split("\n")
                    print ('version: [' + line_bits[0] + ']')
                    
                    if line_bits[0]=='v1':
                        print ('version: ', line_bits[0])
                        print ('command: ', line_bits[1])
                        command_bits=line_bits[1].split(':')
                        command=command_bits[0]
                        
                        if(command=='bulk delete'):
                            deletion_rule=line_bits[2]
                            
                            deletion_date=False
                            if deletion_rule=='3 years old':
                                deletion_date=datetime.now() - relativedelta(years=3)
                                
                            if deletion_rule=='2 years old':
                                deletion_date=datetime.now() - relativedelta(years=2)
                                
                            if deletion_rule=='1 year old':
                                deletion_date=datetime.now() - relativedelta(years=1)
                                
                            if deletion_rule=='6 months old':
                                deletion_date=datetime.now() - relativedelta(months=6)
                                
                            if deletion_rule=='1 month old':
                                deletion_date=datetime.now() - relativedelta(months=1)
                            
                            if deletion_rule=='2 weeks old':
                                deletion_date=datetime.now() - relativedelta(weeks=2)    
                            
                            if deletion_rule=='1 week old':
                                deletion_date=datetime.now() - relativedelta(weeks=1)
                                
                            if deletion_rule=='all':
                                deletion_date=datetime.now()
                                
                            if deletion_date!=False:
                                deletion_date=deletion_date.strftime("%Y-%m-%d")
                                
                                print ("We need to delete records older than", deletion_date)
                                
                                records=run_proc('GET', couchdb_baseurl + '/telemetry/_design/records/_view/all?endkey="' + deletion_date + '"')
                                # Now delete them all...
                                if len(records['rows'])>0:
                                    for json_items in records['rows']:
                                        
                                        try:
                                            ignore=json_items['value']['ignore']
                                        except:
                                            ignore=False;
                                            
                                        if ignore==False:
                                            
                                        
                                            print ('deleting:')
                                            print (json_items)   
                                             
                                            doc_id=json_items['id']
                                            rev=json_items['value']['_rev']
                                            
                                            delete_json=json_items['value']
                                            delete_json['_deleted']=True
                                            
                                            json_string=json.dumps(delete_json);
                                    
                                            #deleted_output=run_proc('PUT', couchdb_baseurl + '/delete_/' + doc_id, json_string)
                                            #updated_doc=run_proc('PUT', couchdb_baseurl + '/telemetry/' + document_id, json_string)
                                            #print (updated_doc) 
                            
    # Now lookfor admin messags for this sensor
    target_subject='System event for ' + wxoutside_sensor_name
    subject=message['subject'][0:len(target_subject)];
    
    if subject==target_subject:
        print ('found a match: ' + subject + ' = ' + target_subject)
        for part in message.walk():
            if part.get_content_type():
                body = part.get_payload(decode=True)
                
                if body is not None:
                    body=body.replace("\n\n", "\n")
                    lines=body.split("\n")
                    if lines[0].split('/')[0]=='v1':
                        print ('command: ', lines[2])
                        command=lines[2];
                          
                        if(command=='bulk delete'):
                            deletion_rule=lines[3]
                            
                            deletion_date=False
                            if deletion_rule=='3 years old':
                                deletion_date=datetime.now() - relativedelta(years=3)
                                
                            if deletion_rule=='2 years old':
                                deletion_date=datetime.now() - relativedelta(years=2)
                                
                            if deletion_rule=='1 year old':
                                deletion_date=datetime.now() - relativedelta(years=1)
                                
                            if deletion_rule=='6 months old':
                                deletion_date=datetime.now() - relativedelta(months=6)
                                
                            if deletion_rule=='1 month old':
                                deletion_date=datetime.now() - relativedelta(months=1)
                            
                            if deletion_rule=='2 weeks old':
                                deletion_date=datetime.now() - relativedelta(weeks=2)    
                            
                            if deletion_rule=='1 week old':
                                deletion_date=datetime.now() - relativedelta(weeks=1)
                                
                            if deletion_rule=='all':
                                deletion_date=datetime.now()
                                
                            if deletion_date!=False:
                                deletion_date=deletion_date.strftime("%Y-%m-%d")
                                
                                print ("We need to delete records older than", deletion_date)
                                
                                records=run_proc('GET', couchdb_baseurl + '/telemetry/_design/records/_view/all?endkey="' + deletion_date + '"')
                                # Now delete them all...
                                if len(records['rows'])>0:
                                    for json_items in records['rows']:
                                        
                                        try:
                                            ignore=json_items['value']['ignore']
                                        except:
                                            ignore=False;
                                            
                                        if ignore==False:
                                        
                                            print ('deleting:')
                                            print (json_items)   
                                             
                                            doc_id=json_items['id']
                                            rev=json_items['value']['_rev']
                                            
                                            delete_json=json_items['value']
                                            delete_json['_deleted']=True
                                            
                                            json_string=json.dumps(delete_json)
                                    
                                            updated_doc=run_proc('PUT', couchdb_baseurl + '/telemetry/' + doc_id, json_string)
                                            print (updated_doc) 
                                                                                        
                        if command=='cancel':
                            print ('sent cancel shudown/restart event!')
                            os.system('sudo shutdown -c')
                        if command=='shutdown':
                            print ('sent system event!')
                            event_time=lines[3]
                            os.system('sudo shutdown -c')
                            os.system('sudo shutdown -h ' + event_time)
                            
                        if command=='restart':
                            print ('sent system event!')
                            event_time=lines[3]
                            os.system('sudo shutdown -c')
                            os.system('sudo shutdown -r ' + event_time)
                            
                        if command=='change soil type':
                            
                            soil_type=lines[4]
                            
                            device=aquaflex_functions.get_device()
                            address=aquaflex_functions.device_address(device)
                            changed=aquaflex_functions.change_soil_type(device, address, soil_type)
        
                            if changed==soil_type:
                                print ('Soil type changed successfully')
                            else:
                                print ('Soil type could not be changed')

        # We need to delete emails os they don't build up...
        print ('deleting email...');
        pop_conn.dele(count);                                       
                
pop_conn.quit()
