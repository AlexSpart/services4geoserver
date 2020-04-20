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

    visualizeVehicles(data_list)

def visualizeVehicles(data_list):

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
    
    #print('ALEX    ',eventtypesJSON)
    #print(json.dumps(pins))
    
    #-----------DISPLAY DATA ON MAP-----------------
    map = folium.Map(location=[45.7797, 3.08682], zoom_start=6) #creates a map centered on France
    
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

    file_name = 'file.txt'
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dest_dir = os.path.join(script_dir, 'templates')
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass # already exists
    path = os.path.join(dest_dir, file_name)

    map.save('./templates/CAM_Map.html')	

    


# main entry point
if __name__ == "__main__":

    run()









