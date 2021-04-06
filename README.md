# jabbermaker
Create cisco jabber profile with a line added and associates to end user


Jabber maker
=============

Jabber maker is Python script that lets you create cisco jabber profiles for PC/MAC, iphone , android and tablet devices.
It will also create a new directory number if user selects to do so.
The script with create the jabber device profile, add a specified line and associate the device to a specified user.


How it does
=============
script uses the Python Zeep SOAP library to read/update CUCM configurations via the AXL SOAP API
Script is adapted from Cisco's DevNet axl-python zeep samples
https://github.com/CiscoDevNet/axl-python-zeep-samples
*It is using the WSDL for CUCM version 11.5


Requirements
===============
- python packages are in the requirments.txt 
- cucm username and password with admin priviliges on cucm
- network reachability to cucm
- download schema folder from repository

You can download the schema folder in repository 

or 

download for your cucm version. 
https://developer.cisco.com/docs/axl/#!download-the-axl-wsdl/download-the-axl-wsdl

The schema folder contains files from the AXL SQL Toolkit.
Follow these steps to download the AXL SQL Toolkit from your Cisco Unified CM server.

   1. Log into the Cisco Unified CM Administration application.

   2. Go to Application | Plugins

   3. Click on the Download link by the Cisco CallManager AXL SQL Toolkit Plugin.

   4. The axlsqltoolkit.zip file contains the complete schema definition for different versions of Cisco Unified CM. 

	    AXLAPI.wsdl
	    AXLEnums.xsd
	    axlmessage.xsd
	    axlsoap.xsd
	    axl.xsd

Then create a folder named 'schema' and add the files AXLAPI.wsdl, AXLEnums.xsd, and axlsoap.xsd


How to Use
===========
You must be run script from same directory location as the schema folder

Edit script to reflect your CUCM environment and run

you will need to edit the variables to match your environment

DEFAULT_PT  = partition used by the directory numbers 
INTERNAL_CSS  = internal seacrh space if applicable
EXTERNAL_CSS = external seacrh space if applicable

you will need to edit the dictionaries 'devicepools' and 'searchspace' to reflect your environmnets device pool names and calling search spaces used by your phones.


devicepools = {'site_a':'devicepool_a',   
               'site_b':'devicepool_b'}

searchspace = {'site_a': 'css_a', 
                'site_b': 'css_b'}

The script has 2 of each to demonstrate options but you can add more or less as applies to you.

You can add more if applicable e.g. 'site_c': 'devicepool_C'
if you do, remember to add extra option to variable 'location' and extra 'if' block, like below

location =  pyip.inputMenu(['For Site_A','For Site_B','For Site_C'], numbered=True)

if location == 'For Site_C':        
    ph_css = searchspace['site_c']
    ph_devicepool = devicepools['site_c']
