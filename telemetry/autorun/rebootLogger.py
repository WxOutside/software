#!/usr/bin/env python

import os
import sys
import time

sys.path.append(os.path.abspath('/home/pi/telemetry/'))
from functions import send_email
from config import wxoutside_sensor_name

date=time.strftime("%Y-%m-%d %H:%M")

print ('Time: ' + str(date))
print ('Code: 100')
print ('Message: System restarted at ' + str(date))

header='v1/' + str(wxoutside_sensor_name) + "/system event/" + str(date) + "\n"
body="Action: system restarted\n"
body=body + + 'Time: ' + str(date) + "\n";
body=body + 'Message: System restarted at ' + str(date) + "\n"

send_email('System event response', header + body)