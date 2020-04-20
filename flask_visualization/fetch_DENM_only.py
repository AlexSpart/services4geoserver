import requests
import json
import folium
import webbrowser
import os

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
map = folium.Map(location=[45.7797, 3.08682], zoom_start=6) #creates a map centered on France


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


file_name = 'file.txt'
script_dir = os.path.dirname(os.path.abspath(__file__))
dest_dir = os.path.join(script_dir, 'templates')
try:
    os.makedirs(dest_dir)
except OSError:
    pass # already exists
path = os.path.join(dest_dir, file_name)

map.save('./templates/DENM_Map.html')

#automatic opening
#new = 2 # open in a new tab, if possible
#url = 'file://' + os.path.abspath('Map.html') #find the absolute path of the saved file

#webbrowser.open(url,new=new)


