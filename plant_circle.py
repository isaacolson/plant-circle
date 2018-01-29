#!/usr/bin/env python
"""Plant Circle Farmware"""

import os
import json
import base64
import math
import requests

def log(message, message_type):
    'Send a message to the log.'
    log_message = '[plant-circle] ' + str(message)
    headers = {
        'Authorization': 'bearer {}'.format(os.environ['FARMWARE_TOKEN']),
        'content-type': "application/json"}
    payload = json.dumps(
        {"kind": "send_message",
            "args": {"message": log_message, "message_type": message_type}})
    requests.post(os.environ['FARMWARE_URL'] + 'api/v1/celery_script',
                    data=payload, headers=headers)

def get_env(key, type_=int):
    'Return the value of the namespaced Farmware input variable.'
    return type_(os.environ['{}_{}'.format(farmware_name, key)])

class Circle():
    'Add a circle of plants to the farm designer.'
    def __init__(self):
        API_TOKEN = os.environ['API_TOKEN']
        self.headers = {'Authorization': 'Bearer {}'.format(API_TOKEN),
                        'content-type': "application/json"}
        encoded_payload = API_TOKEN.split('.')[1]
        encoded_payload += '=' * (4 - len(encoded_payload) % 4)
        json_payload = base64.b64decode(encoded_payload).decode('utf-8')
        server = json.loads(json_payload)['iss']
        self.api_url = 'http{}:{}/api/'.format(
            's' if not any([h in server for h in ['localhost', '192.168.']])
            else '', server)

    def add_plant(self, x, y):
        'Add a plant through the FarmBot Web App API.'
        plant = {'x': str(x), 'y': str(y),
                 'radius': str(size),
                 'name': name, 'pointer_type': 'Plant', 'openfarm_slug': slug}
        payload = json.dumps(plant)
        r = requests.post(self.api_url + 'points',
                          data=payload, headers=self.headers)

    def add_plants(self):
        'Find max number of plants and add them to the farm designer.'
        circumference = 2*math.pi*(diameter/2)
        num_plants = math.floor(circumference/min_dist)
        sep_angle = 360/num_plants
        
        count = int(num_plants)
        
        for i in range(count):
            angle = i*((math.pi/180)*sep_angle)
            x_adjust = math.cos(angle)*(diameter/2)
            y_adjust = math.sin(angle)*(diameter/2)
            self.add_plant(x_pos + x_adjust, y_pos + y_adjust)
        log('{} plants added.'.format(int(num_plants)),
            'success')

if __name__ == '__main__':
    farmware_name = 'plant_circle'
    # Load inputs from Farmware page widget specified in manifest file
    x_pos = get_env('x_pos')
    y_pos = get_env('y_pos')
    diameter = get_env('diameter')
    min_dist = get_env('min_dist')
    size = get_env('size')
    name = get_env('name', str)
    slug = get_env('slug', str)
    
    circle = Circle()
    circle.add_plants()
