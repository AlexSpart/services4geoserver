import requests
import json
import folium
import webbrowser
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
    map = folium.Map(location=[45.7797, 3.08682], zoom_start=6) #creates a map centered on France
    fetch_cam(map)
    fetch_denm(map)


    file_name = 'file.txt'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, 'templates')
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass # already exists
    path = os.path.join(dest_dir, file_name)

    map.save('./templates/all_Map.html')

def fetch_denm(map):
    #-------------------MAKING THE REQUEST------------------------#
    URL = 'https://5gcroco.eurecom.fr:442/n/databaseDump?collection=denm' #url of geoserver
    headers = {} #credentials infos

    req = requests.get(URL, verify=False)  #, headers)

#-------------------PROCESSING---------------------------------#
    data = req.json() #returns a dict

    #doing some further processing
    pins = dict()
    data_list = data["denm"] #fetching data of denm db, list of data
    eventtypes = set()


    for item in data_list:
        print(item)
        #item is a json having the singular message
        event = item['message']['situation_container']['event_type']
        coordinates = [item['message']['management_container']['event_position']['latitude'], item['message']['management_container']['event_position']['longitude']] 

        #we check that there is no duplicate event
        if [coordinates, event] not in pins.values():
    	    #we don't want duplicate alerts
            pins[item['_id']] = [coordinates, event]
            #eventtypes.add(event)
            eventtypesJSON = json.dumps(event)
    #print('print event types:    ',eventtypesJSON)
    #print(json.dumps(pins))

#-----------DISPLAY DATA ON MAP-----------------


    for key,pin in pins.items():
	    pin[0] = [i / 10000000 for i in pin[0]]
	    folium.Marker(pin[0],
					popup="<b>id:</b> {0},</br><b>eventType:</b>{1},<br/> <b>coordinates:</b> {2}".format(key,pin[1],pin[0]),
					icon=folium.Icon(color="red",icon="warning", prefix='fa')).add_to(map)

	    #display event type: 94 (road work), 99 (emergency break), 10,..

    #------------------RoI-----------------------
    #Map that displays all the markers AND the reagion of interest, no duplicates entries (MAC address)
    #RoI : (lat, long) + radius
    req = requests.get('https://5gcroco.eurecom.fr:442/n/allsubscriptions', verify=False)  #, headers)

    #-------------------PROCESSING---------------------------------#
    data = req.json()
    rois_list = data["subscription"]
    circles = dict()

    for item in rois_list:
	    #print(item)
	    coordinates = item['roi'].split(',')
	    circles[item['macAddress']] = [coordinates, item['radius']]

    #print(circles)

    for key, roi in circles.items():
	    folium.Circle(location=roi[0],
						radius=roi[1],
						popup="<b>MAC:</b> {0},<br/><b>center:</b> {1},<br/><b>radius:</b> {2} m".format(key, roi[0], roi[1]),
						color='#3186cc',
    					fill=True,
    					fill_color='#3186cc').add_to(map)


 


def fetch_cam(map):
    
    #-------------------MAKING THE REQUEST------------------------#
    URL = 'https://5gcroco.eurecom.fr:442/n/databaseDump?collection=cam' #url of geoserver
    headers = {} #credentials infos
    req = requests.get(URL, verify=False)  #, headers)
    #-------------------PROCESSING---------------------------------#
    data = req.json() #returns a dict
    #doing some further processing
    pins = dict()
    data_list = data["cam"] #fetching data of denm db, list of data
    eventtypes = set()

    visualizeVehicles(data_list,map)

def visualizeVehicles(data_list,map):

    for item in data_list:
       # print(item)
        #item is a json having the singular message
        speed = item['message']['high_frequency_container']['speed']
        coordinates = [item['message']['basic_container']['reference_position']['latitude'], item['message']['basic_container']['reference_position']['longitude']] 
        
        #we check that there is no duplicate event
        if [coordinates, speed] not in pins.values():
        	#we don't want duplicate alerts
            pins[item['_id']] = [coordinates, speed]
            #eventtypes.add(event)
            eventtypesJSON = json.dumps(speed)
    
    #-----------DISPLAY DATA ON MAP-----------------

    for key,pin in pins.items():
                                        pin[0] = [i / 10000000 for i in pin[0]]
                                        #folium.Marker(pin[0],
    					#popup="<b>id:</b> {0},</br><b>speed:</b>{1},<br/> <b>coordinates:</b> {2}".format(key,pin[1],pin[0]),
    					#icon=folium.Icon(color="darkblue",icon="car", prefix='fa')).add_to(map)

                                        #folium.Circle(location=pin[0],radius=1,popup="<b>id:</b> {0},</br><b>speed:</b>{1},<br/> <b>coordinates:</b> {2}".format(key,pin[1],pin[0]),
                                        #color='crimson',fill=True).add_to(map)
                                        folium.CircleMarker(location=pin[0],radius=2,popup="<b>id:</b> {0},</br><b>speed:</b>{1},<br/> <b>coordinates:</b> {2}".format(key,pin[1],pin[0]),
                                        color='darkblue',fill=True,fill_opacity=1).add_to(map)
    #display event type: 94 (road work), 99 (emergency break), 10,..
    #-------------------------------------------------#


# main entry point
if __name__ == "__main__":

    run()










