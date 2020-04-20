import flask
import os
import webbrowser
from flask import render_template

#from selenium import webdriver
#from selenium.webdriver import Chrome



app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "<h1>Visualization of messages</h1><p>Visit http://127.0.0.1:5000/visualize_DENM for DENM.</p><p>Visit http://127.0.0.1:5000/visualize_CAM for CAM.</p><p>Visit http://127.0.0.1:5000/visualize_all for all combined.</p"

@app.route('/visualize_DENM', methods=['GET'])
def visualize_DENM():

        os.system('python3 fetch_DENM_only.py')
        return render_template('DENM_Map.html')


@app.route('/visualize_CAM', methods=['GET'])
def visualize_CAM():

        os.system('python3 fetch_CAM_only.py')
        return render_template('CAM_Map.html')

@app.route('/visualize_all', methods=['GET'])
def visualize_all():

        os.system('python3 fetch_all.py')
        return render_template('all_Map.html')



app.run()


