# Weather sensor software
This respository contains all the software you need to run the hardware described in the accompanying hardware repository.

It is designed to run on a Raspberry Pi A+, but will also work on a Raspberry Pi 2, 3 and presumably a Zero (not tested).

Operating system download
=========================

First, we need to download the OS and flash this onto the SD card that the RPi unit uses.
We use Jessie-lite because it only includes the basic components - for example we don't need the desktop. And the A+ can run into stability issues when too many processes are running.

- *Step 1:* Download Jessie-lite: https://www.raspberrypi.org/downloads/raspbian/
- *Step 2:* Install Jessie-lite, as described here: https://www.raspberrypi.org/documentation/installation/installing-images/mac.md

OS X steps only:
----------------

*Note*: steps for other operating systems are provided in the Raspberry Pi links above

- Unmount the SD card via disk utility
  - Take note of the disk number - you'll need that for the command in the next step
- In terminal, run the following command (using the actual file name, and replacing YOURNAME with the path to your downloads directory)
  - Also, replace 'disk3' with the disk number from the previous step

  ```bash
  sudo dd bs=1m if=/Users/YOURNAME/Downloads/2016-03-18-raspbian-jessie-lite.img of=/dev/rdisk3
  ```

Operating system setup
======================

You'll need to have a monitor connected to the RPi for this step, but afterwards you can use a network connection.

**By default, the username will be 'pi' and the password is 'raspberry'**

- Step 3: Run raspsi-config and set a machine name and auto-login and password

  ```bash
  sudo raspi-config
  ```
  - User password is located in option 2
  - Machine name is located in Advanced settings -> A2 Hostname
  - Enable SSH: Go to 'Interfacing Options' -> P2 SSH -> Yes
  - While you're there, set the timezone to NZDT (or your local timezone): Internationalisation options -> I2 Change Timezone

**You can now access this via the network** via ssh pi@MACHINE_NAME (where MACHINE NAME is what you just set up)

- *Step 4:* Update the operating system
  ```bash
  sudo apt-get update
  ```
  
- *Step 5:* Upgrade any components
  ```bash
  sudo apt-get upgrade
  ```

- *Step 6:* Install CouchDB. This isn't the latest version, but it's guaranteed to work with Jessie, and it's enough for what we need.
  ```bash
  sudo aptitude install couchdb
  ```

- *Step 7:* Update the CouchDB ini settings to use the generic address. This allows us to access it remotely. 
  ```bash
  sudo pico /etc/couchdb/local.ini
  ```
  change bind address to bind_address = 0.0.0.0
    
  then restart the service (just to make sure it's all working): 
  ```bash
  sudo /etc/init.d/couchdb restart
  ```

- *Step 8:* Set up basic Python and I2C bits.
  ```bash
  sudo apt-get install python-smbus
  sudo apt-get install i2c-tools
  sudo raspi-config
  ```
  Go to 'Interfacing Options' -> P5 I2C -> Yes -> Ok
  
  Exit raspi-config and now reboot:
  ```bash
  sudo reboot
  ```

- *Step 9:* Disable the HDMI port. This will save ~20mA when idling, and we don't need the monitor connection anymore.
  ```bash
  sudo pico /etc/rc.local
  ```
  Add these lines:
  ```
  # WxOutside: turn off the HDMI port:
  /opt/vc/bin/tvservice -o
  ```
  If you ever want to connect a monitor again, remove this line and reboot

Sensor support
==============

- *Step 9:* Install pip:
  ```bash
  sudo apt-get install python-pip
  sudo apt-get install python3-pip
  sudo pip3 install RPi.GPIO 
  sudo pip install python-dateutil
  ```
  
- *Step 9:* Set up support for the am2315 sensor - this will take a long time, the download is very slow for some reason.
  ```bash
  sudo pip3 install --process-dependency-links aosong
  ```
- *Step 10:* Set up support for the aquflex sensor. The script will support both Python 3.x and 2.x, but we'll settle for version 2.
  ```bash
  sudo apt-get install python-serial
  ```

- *Step 11:* 3G dongle support. Steps taken from here: https://www.raspberrypi.org/forums/viewtopic.php?t=18996
  This will work for the e3131, any other dongle will need the equivalent file contents.
  ```bash
  sudo apt-get install sg3-utils
  ```
  create a new file "/etc/udev/rules.d/10-HuaweiFlashCard.rules" with the following content:
  ```
  SUBSYSTEMS=="usb", ATTRS{modalias}=="usb:v12D1p1F01*", SYMLINK+="hwcdrom", RUN+="/usr/bin/sg_raw /dev/hwcdrom 11 06 20 00 00 00 00 00 01 00"
  ```
  
  Now configure the network interfaces to support this:
  ```bash
  sudo pico /etc/network/interfaces
  ```
  edit eth0 to say this:
  ```bash
  allow-hotplug eth0
  iface eth0 inet dhcp
  ```

  And now reboot:
  ```bash
  sudo reboot
  ```

Code support
============

- *Step 12:* Create a directory called 'telemetry' in the pi user location:
  ```bash
  cd ~/
  mkdir telemetry
  ```
  
  Copy over all the sensor code from the latest release here: https://github.com/WxOutside/software/releases

- *Step 13:* Set up weatherPiArduino
  ```bash
  cd ~/telemetry/sensors/weatherPiArduino
  chmod u+x weatherPiArduino_agent.py
  ```

Database support
================

In a browser, go to http://MACHINE_NAME.local:5984/_utils, where MACHINE_NAME is what you set in step 3.

- Step 14: create database called “telemetry”
  - Create a design document called 'records', with a view name called 'unsent', with the following map function:
  
  ```javascript
  function(doc) {
    if(!doc.ignore && !doc.email_sent){
      emit(doc._rev, doc)
    }
  }
  ```
- Step 15: create a database called 'hardware' with a design document titled with your machine name (MACHINE_NAME)
  - this can be left empty, it will be automatically populated
  
Crontab entries
===============

- Step 16: create entries in the crontab so telemetry readings will be taken and transmitted out:
  ```bash
  crontab -e
  ```
  
  Then added these lines:

  ```
 # Run sensors:
1 * * * * /usr/bin/python3 /home/pi/telemetry/sensors/am2315.py > /home/pi/telemetry/logs/am2315.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1
1 * * * * /usr/bin/python /home/pi/telemetry/sensors/aquaflex.py > /home/pi/telemetry/logs/aquaflex.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1
2 * * * * /usr/bin/python /home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_controller.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1

# minute 10 reserved for hardware stats
30 * * * * /usr/bin/python3 /home/pi/telemetry/sensors/am2315.py > /home/pi/telemetry/logs/am2315.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1
31 * * * * /usr/bin/python /home/pi/telemetry/sensors/weatherPiArduino/weatherPiArduino_controller.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1

# Notifications:
51 * * * * /usr/bin/python /home/pi/telemetry/cron/sendHardwareStats.py > /home/pi/telemetry/logs/sendHardwareStats.log 2>&1
55 * * * * /usr/bin/python /home/pi/telemetry/cron/sendTelemetry.py > /home/pi/telemetry/logs/sendTelemetry.log 2>&1
50 * * * * /usr/bin/python /home/pi/telemetry/cron/checkEmail.py > /home/pi/telemetry/logs/checkEmail.log 2>&1

# System hygiene scripts:
5 2 * * * /usr/bin/python /home/pi/telemetry/cron/updateCode.py > /home/pi/telemetry/logs/updateCode.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1
10 * * * * /usr/bin/python /home/pi/telemetry/cron/hardwareStats.py > /home/pi/telemetry/logs/hardwareStats.log 2>&1
10 * * * * /usr/bin/python /home/pi/telemetry/cron/logger.py > /home/pi/telemetry/logs/logger.log 2>&1
30 3 * * * bash /home/pi/telemetry/cron/compaction.sh int > /home/pi/telemetry/logs/compaction.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1

@reboot /usr/bin/python /home/pi/telemetry/autorun/rebootLogger.py > /home/pi/telemetry/logs/rebootLogger.`date +\%Y\%m\%d\%H\%M\%S`.log 2>&1
  ```

Credits
=======

The weatherPiArduino hardware uses a slightly modified version of the weatherPiArduino libraries, provided by SwitchDoc Labs
https://github.com/switchdoclabs/RaspberryPi-WeatherPiArduino

AM2315 sensor class comes from Sopwith http://sopwith.ismellsmoke.net/?p=104

Aquaflex code written with assistance from Streats Instruments http://www.streatsahead.com

