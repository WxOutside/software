# How to use these files

Copy this entire /telemetry directory into your ~pi user directory.
You can put it elsewhere, but you'll need to change the paths in a few scripts (no big deal).

All scripts should be run via the user crontab, or can be run from the command line using Python.

Things to change
================

You'll need to edit the config file to use valid connection settings.
If you plan to use the WxOutside service to display the telemetry and include weather forecasts, then you'll need to request an account.
Please email geoff@wxoutside.tools to arrange this.

You can change these settings to use any other service you want, but you'll probably have to customise the format of the messages and the endpoint settings.
