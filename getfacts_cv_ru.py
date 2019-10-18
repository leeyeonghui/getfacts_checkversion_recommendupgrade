#!/usr/bin/env python
#Author = Lee Yeong Hui

from pprint import pprint 
from jnpr.junos import Device
from os.path import dirname, join
from datetime import datetime
import getpass
import yaml
import sys

try:
    userID = raw_input("Enter username: ")
except: 
    userID = input("Enter username: ")
userPW = getpass.getpass("Enter password: ")

# Get relative directory 
currentDir = dirname(__file__)

# Get hosts.yml relative directory 
filePath = join(currentDir, "hosts.yml")

# Read hosts.yml
with open(filePath, 'r') as rd:
	hosts = yaml.load (rd.read())

# Get versions.yml relative directory
filePath = join(currentDir, "versions.yml")

# Read versions.yml 
with open(filePath,'r') as rd: 
    versions = yaml.load (rd.read())

aListofDevice = []
# Connect to each device to get data 
for host in hosts: 
    try:
        print('Initiating Check on ' + host)
        #use port 22 if 830 does not work/set system services netconf ssh is not configured
        dev = Device(host=host, user=userID, password=userPW, port="22") 
        dev.open()
        # print all facts
        #pprint(dev.facts)
        aDevice = {
          'model' : dev.facts['model'], 
          'hostname' : dev.facts['hostname'],
          'serialnumber' : dev.facts['serialnumber'],
          'uptime' : dev.facts['RE0']['up_time'],
          'cursoftware' : dev.facts['version'],
          'desiresoftware' : '',
          'softwarechangerequired' : 'yes'
        }
        print ('Data collected from ' + host)
        aListofDevice.append(aDevice)
    except Exception as e:
        print (e)

# compare versions 
for device in aListofDevice:
    for model in versions:
        if model['model'] == device['model']:
            device['desiresoftware'] = model['version']
            if model['version'] == aDevice['cursoftware']:
                device['softwarechangerequired'] = 'no' 

# print output on terminal 
print ('\n\nTotal hosts were checked: %d' % (len(hosts)))
print ('-' * 200)
print ('HOSTNAME\t\t\tMODEL\t\tS/NUMBER\t\tCURRENT_SW\t\tDESIRE_SW\tSOFTWARE_CHG_REQUIRED\tUPTIME')
print ('-' * 200)

# print output to txt
# get current date time 
currentDateTime = datetime.now()
# Get hosts.yml relative directory 
fileName = '{:%d-%b-%y-%H-%M}-getfacts.txt'.format(currentDateTime)
filePath = join(currentDir, fileName)
outputFile = open(filePath,"w")
outputFile.write ('Total hosts were checked: %d\n' % (len(hosts)))
outputFile.write ('-' * 200 + '\n')
outputFile.write('HOSTNAME\t\t\tMODEL\t\tS/NUMBER\t\tCURRENT_SW\t\tDESIRE_SW\tSOFTWARE_CHG_REQUIRED\tUPTIME\n')
outputFile.write ('-' * 200 + '\n')

# for device in sorted(aListofDevice, key = lambda i:i['softwarechangerequired']): / list no software change required first 
# reverse direction / list need software change required first 
for device in sorted(aListofDevice, key = lambda i:i['softwarechangerequired'], reverse=True):
    print ('%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s' % (device['hostname'], device['model'], device['serialnumber'], device['cursoftware'], device['desiresoftware'], device['softwarechangerequired'], device['uptime']))
    outputFile.write('%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\t\t%s\n' % (device['hostname'], device['model'], device['serialnumber'], device['cursoftware'], device['desiresoftware'], device['softwarechangerequired'], device['uptime']))
print ('-' * 200)

# close outputFile
outputFile.close()