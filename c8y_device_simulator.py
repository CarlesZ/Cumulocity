'''
Cumulocity Device Simulator - HTTP/JSON based 
Please refer to the documentation for further details on the API:
https://cumulocity.com/guides/reference/rest-implementation/

'''

import requests
from requests.auth import HTTPBasicAuth
import json
import datetime
import random
from threading import Thread
from time import sleep

host = 'https://TENANT.cumulocity.com'
username = 'testuser'
password = 'password'

auth = HTTPBasicAuth(username, password)
session = requests.Session()
session.auth = auth
session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/json'
                })


SENSOR_READING_TIME_DELAY = 10.0
INITIAL_SENSOR_VALUE = 100.0
POSITIVE_CHANGE_PROBABILITY = 0.5

class DeviceDescription:
    
    c8y_id = "" # this will be given when we create and register device
    
    def __init__(self, name, type, measurementType, measurementName, measurementUnit):
        self.name = name
        self.type = type
        self.measurementType = measurementType
        self.measurementName = measurementName
        self.measurementUnit = measurementUnit


sensorDevices = [ DeviceDescription("TempSensor-1", "TemperatureSensor", "c8y_Temperature", "T", "C"), 
                  DeviceDescription("PressureSensor-1", "PressureSensor", "c8y_Pressure", "P", "Pa") ]


def createDevice(name, id, measurementName):
    return

def createMeasurement(deviceDescription, value):
    measurementData = {}
    measurementData['source'] = { "id" : deviceDescription.c8y_id }
    measurementData['time'] = formatTimestamp(datetime.datetime.utcnow())
    measurementData['type'] = deviceDescription.measurementType
    measurementData[deviceDescription.measurementType] = { deviceDescription.measurementName : { "value": value, "unit" : deviceDescription.measurementUnit } }
    #print (json.dumps(measurementData, indent = 4))
    status = submitMeasurement(measurementData)
    print("Measurement submitted for deviceId='%s' value='%s' ... result -> %s"%(deviceDescription.c8y_id, value, status))

def sensorLifecycle(deviceDescription):
    value = INITIAL_SENSOR_VALUE*random.random()
    while True:
        delta = (INITIAL_SENSOR_VALUE * 0.10)*random.random()
        sleep(SENSOR_READING_TIME_DELAY)
        
        if POSITIVE_CHANGE_PROBABILITY > random.random():
            value += delta
        else:
            value -= delta 
        createMeasurement(deviceDescription, value)
            
def generateSimulatedMeasurements():
 
    for deviceDescription in sensorDevices:
        if deviceDescription.c8y_id == None:
            print("Ignoring device with no managed object -> " + deviceDescription.name)
            continue
        
        thread = Thread(target=sensorLifecycle, args=(deviceDescription, ))
        thread.start()
        print ("Lifecycle for sensor '%s' with id='%s' started."% (deviceDescription.name, deviceDescription.c8y_id))
    
            
def formatTimestamp(timestamp):
    return timestamp.isoformat(timespec='milliseconds')

 
def submitMeasurement(measurementJson):
    session.headers.update({
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.com.nsn.cumulocity.measurement+json'
                })
    url = host + '/measurement/measurements'
    response = session.post(url, json=measurementJson)
    #print(str(response.text))
    return response.status_code
    

if __name__ == "__main__":
    for deviceDescription in sensorDevices:
        deviceDescription.c8y_id = checkAndRegisterDevice(deviceDescription.name, deviceDescription.type, deviceDescription.name)
        
    generateSimulatedMeasurements()

