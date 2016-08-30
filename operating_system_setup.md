Operating system download
=========================

First, we need to download the OS and flash this onto the SD card that the RPi unit uses.
We use Jessie-lite because it only includes the basic components - we don't need the desktop for instance. And the A+ can run into stability issues when too many processes are running.

- *Step 1:* Download Jessie-lite: https://www.raspberrypi.org/downloads/raspbian/
- *Step 2:* Install Jessie-lite, as described here: https://www.raspberrypi.org/documentation/installation/installing-images/mac.md

OS X steps only:
----------------

*Note*: steps for other operating systems are provided in the Raspberry Pi links above

- Unmount the SD card via disk utility
  - Take note of the disk number - you'll need that for the commandin the next step
- In terminal, run the following command (using the actual file name, and replacing YOURNAME with the path to your downloads directory)
  - Also, replace 'disk3' with the disk number from the previous step

  ```bash
  sudo dd bs=1m if=/Users/YOURNAME/Downloads/2016-03-18-raspbian-jessie-lite.img of=/dev/rdisk3
  ```

Operating system setup
======================

You'll need to have a monitor connected to the RPi for this step, but afterwards you can use a network connection.

- Step 3: Run raspsi-config and set a machine name and auto-login and password
  ```bash
  sudo raspi-config
  ```
  - While you're there, set the timezone to NZDT (or your local timezone)

**You can now access this via the network**

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
    
  then restart service: 
  ```bash
  sudo /etc/init.d/couchdb restart
  ```

- *Step 8:* Set up basic Python and I2C bits.
  ```bash
  sudo apt-get install python-smbus
  sudo apt-get install i2c-tools
  sudo raspi-config
  ```
  Go to 'Advanced' -> A7 I2C -> Yes -> Ok -> Yes -> Ok
  
  Now reboot:
  ```bash
  sudo reboot
  ```

- *Step 9:* Disable the HDMI port. This will save ~20mA when idling, and we don't need the monitor connection anymore.
  ```bash
  sudo pico /etc/rc.local
  ```
  Add these lines:
  ```
  # WxOutside: turn off the HDML port:
  /opt/vc/bin/tvservice -o
  ```

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

- *Step 10:* 3G dongle support. Steps taken from here: https://www.raspberrypi.org/forums/viewtopic.php?t=18996
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
  edit eth0 to say this:
  allow-hotplug eth0
  iface eth0 inet dhcp
  ```

  And now reboot:
  ```bash
  sudo reboot
  ```

Code support
============

- *Step 11:* Create a directory called 'telemetry' in the pi user location:
  ```bash
  cd ~\pi
  mkdir telemetry
  ```
  
  Copy over all the sensor code
  @TODO - include link to code in GitHub

- *Step 12:* Set up weatherPiArduino
  ```bash
  cd ~\telemetry\sensors\weatherPiArduino
  chmod u+x weatherPiArduino_agent.py
  ```
Database support
================

In a browser, go to http://MACHINE_NAME.local:5984, where MACHINE_NAME is what you set in step 3.

- *Step 13:* create database called “config”
- *Step 14:* add record called “sensors”
- *Step 15:* add the following fields:
  ```
  soil_probe_light: False
  soil_probe_moisture: True
  soil_probe_temperature: True
  ```

- Step 16: create database called “telemetry”
