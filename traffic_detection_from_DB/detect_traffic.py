import requests
import json
import os
import socket
import math
import numpy
from geopy.distance import geodesic

maxDistanceDict=dict() # distance between a given vehicle and the furthest vehicles
closeVehiclesDict=dict() # number of neighbour's vehicles
density=dict() # store the value of the density calculate by each vehicle

pins = dict()

def run():

    #-------------------MAKING THE REQUEST------------------------#
    URL = 'https://5gcroco.eurecom.fr:442/n/databaseDump?collection=cam' #url of geoserver
    headers = {} #credentials infos
    req = requests.get(URL, verify=False)  #, headers)
    #-------------------PROCESSING---------------------------------#
    data = req.json() #returns a dict
    #doing some further processing
    pins = dict()
    global data_list
    data_list = data["cam"] #fetching data of denm db, list of data
    eventtypes = set()

    trafficJamDetector(data_list)

def trafficJamDetector(data_list):
    vehiclesSpeed = dict()
    vehiclesCoor = dict()
    vehiclesAngle = dict()
    counter = 0
    print("the length of the data_list is:  ")
    print(len(data_list))
     #put speeds and positions in dictionaries
    for i in data_list:
        vehiclesSpeed[counter] = i['message']['high_frequency_container']['speed']/100
        #print("SPEED IS -------> ",vehiclesSpeed[counter])
        vehiclesAngle[counter] = i['message']['high_frequency_container']['heading']/10
        #print("HEADING IS -------> ",vehiclesAngle[counter])
        converted_lon = (i['message']['basic_container']['reference_position']['longitude']/10000000)
        #print(converted_lon)
        converted_lat = (i['message']['basic_container']['reference_position']['latitude']/10000000)
        #print(converted_lat)
        vehiclesCoor[counter] = [converted_lon,converted_lat] 
        #print(vehiclesCoor[counter])
        counter += 1
    #print(vehiclesSpeed)
    #print(vehiclesAngle)
    #print(vehiclesCoor)
    closeVehicles(vehiclesSpeed, vehiclesCoor, vehiclesAngle)

def closeVehicles(speed = dict(), coor = dict(), angle = dict()):

    #print(speed)
    for key1 in coor:
        closeVehicles=0
        maxDistanceDict[key1] = 0
        maxDistanceFront=0
        maxDistanceBack=0

        for key2 in coor:
            # calculate the distance between two vehicles
            distance = geodesic(coor[key1], coor[key2]).m  #this method is used for coordinates (lat,lon) as input
            #distance=math.sqrt((coor[key1][0]-coor[key2][0])**2 + (coor[key1][1]-coor[key2][1])**2)

            # calculate the angle between two vehicles
            direction=math.atan2(coor[key2][1]-coor[key2][0], coor[key1][1]-coor[key1][0])

            if distance<100 and key1!=key2: # if the vehicles are close enough

                if angle[key2]>angle[key1]-25 and angle[key2]<angle[key1]+25: #if the vehicles drive in same direction
                    closeVehicles = closeVehicles+1 # increment the number of close vehicles

                    if direction>0: # if the vehicle is in front of the given vehicle

                        if distance > maxDistanceFront: # if the distance between them is higher than the max distance in front
                            maxDistanceFront = distance

                    else: # if the vehicle is behind

                        if distance > maxDistanceBack: # if the distance between them is higher than the max distance behind
                            maxDistanceBack = distance

        maxDistanceDict[key1]=maxDistanceFront+maxDistanceBack # calculate the total distance between the two furthest vehicles
        closeVehiclesDict[key1]=closeVehicles # store the number of neighbours' vehicles
    densityCalculation(maxDistanceDict, closeVehiclesDict)

def densityCalculation(distanceMax = dict(), closeVeh = dict()):
    numberOfLanes=3   #the algorithm needs to know the number of lanes in order to compute the density. Since it's not yet available from the db we hard code it depending on the scenario.
    speedlimit= 100   #the algorithm needs to know the speed limit.. since it's ment not available and it's supposed to be used for highway we hardcopy 100 for the moment
    for key in closeVeh:
        #print(" DATA_LIST[KEY] --------->>>>>>>")
        #print(data_list[key])
        if distanceMax[key] != 0: # avoid division by zero
            density[key]=((closeVeh[key]/numberOfLanes)*1000)/(distanceMax[key]) # calculation of the density around the vehicle

            #if traci.vehicle.getAllowedSpeed(key)*0.62>traci.vehicle.getSpeed(key): # if the speed of the vehicle is less than 62% of the allowed speed
            print("Density around the vehicle is --------> ", density[key])
            if density[key]>50:			    # if the density is higher than 50
                print("Assign vehicle as RED")
                send_DENM_message(data_list[key])    #SEND a DENM message if the vehicle is RED

            if density[key]>37 and density[key]<50: # if the density is included between 37 and 50
                print("Assign vehicle as ORANGE")

            if density[key]>29 and density[key]<37: #if the density is included between 29 and 37
                print("Assign vehicle as YELLOW")

            if density[key]<29:        		    # if the density is less than 29
                print("Assign vehicle as FREEN")

def send_to_quadkeymapper(mydata):
    json_data = json.dumps(mydata)
    server_address_tx = "/tmp/QUADKEY_SAP"
    server_address_rx = "/tmp/QUADKEY_SAP_client"

    print('Sending data for convert to quadkey ------- ', json_data )
    #print('connecting to {}'.format(server_address_rx))
    if os.path.exists( server_address_rx ):
        os.remove( server_address_rx )
    client_rx= socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)  #Creating a blocking socket /tmp/QUADKEY_SAP_client to receive the converted value
    client_rx.bind(server_address_rx)                            #and bind to it so that 

    print('connecting to {}'.format(server_address_tx))
    if os.path.exists(server_address_tx):
        client_tx= socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) #Connecting to the socket /tmp/QUADKEY_SAP
        client_tx.connect(server_address_tx)			#and send the data so the conversion is done
        client_tx.send(json_data.encode('utf-8'))
        client_tx.close()
    del json_data

    datagram = client_rx.recv(1024)
    #print("The converted string is ----->",datagram.decode('utf-8')) #Use the converted quadkey later to compose a DENM....
    return(datagram.decode('utf-8'))

def send_DENM_message(cam_info):
    #print(" cam_info --------->>>>>>>")
    #print(cam_info)   #cam info message from which the DENM was triggered
		      #we use some of the info such as position etc. to compose a new DENM as traffic jam was detected at that position
    lon = cam_info['message']['basic_container']['reference_position']['longitude']
    #print("PUT IN DENM THIS LON",lon)
    lat = cam_info['message']['basic_container']['reference_position']['latitude']
    #print("PUT IN DENM THIS LAT",lat)
    speed = cam_info['message']['high_frequency_container']['speed']/100
    #print("PUT IN DENM THIS speed.... m/s...",speed)

    data_to_quad = {"latitude":lat, "longitude":lon, "direction":"1", "zoom":"22"}
    quad_output = send_to_quadkeymapper(data_to_quad)         #add it later in tHe DENM......
    print("Converted quadkey: ",quad_output)

    data = json.loads(quad_output)
    quad_code=data['quad']                          #use the quad_code to insert it in the DENM....
    direction_code=data['direction']
    #print(quad_code,type(quad_code))
    #print(direction_code,type(direction_code))
    
    
    DENM_message = {
  "type": "denm",
  "origin": "self",
  "version": "1.0.0",
  "source_uuid": "uuid14",
  "mac": "detect_traffic_jam_script",
  "timestamp": 1574778515425,
  "message": {
    "protocol_version": 1,
    "station_id": 42,
    "management_container": {
      "action_id": {
        "originating_station_id": 41,
        "sequence_number": 1
      },
      "detection_time": 503253332000,
      "reference_time": 503253330000,
      "event_position": {
        "latitude": lat,
        "longitude": lon,
        "altitude": 20000
      },
      "validity_duration": 600,
      "station_type": 5,
      "confidence": {
        "position_confidence_ellipse": {
          "semi_major_confidence": 100,
          "semi_minor_confidence": 50,
          "semi_major_orientation": 180
        },
        "altitude": 3
      }
    },
    "situation_container": {
      "event_type": {
        "cause": 97,
        "subcause": 0
      }
    },
    "location_container": {
      "event_speed": 289,
      "event_position_heading": 1806,
      "traces": [
        {
          "path_history": []
        }
      ],
      "confidence": {
        "speed": 3,
        "heading": 2
      }
    }
  }
}
           		
    json_data = json.dumps(DENM_message)
    #print(json_data)
    # print("THE SIZE OF WHAT I SEND IS:",sys.getsizeof(json_data))
    server_address = "/tmp/DEVM_SAP"
    print('connecting to {}'.format(server_address))
    #print('Sending data for PASSENGER TIME_STEP: {}'.format(timestep))
    if os.path.exists(server_address):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        client.connect(server_address)
        client.send(json_data.encode('utf-8'))
        client.close()
    del json_data

# main entry point
if __name__ == "__main__":

    run()











