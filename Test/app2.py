# -*- coding: utf-8 -*-

import pandas as pd
from shapely.geometry import Point, shape

from flask import Flask
from flask import render_template
import json


data_path = './input/'
n_samples = 30000

#def severity_segment(age):
#    if age <= 22:
#        return '22-'
#    elif age <= 26:
#        return '23-26'
#    elif age <= 28:
#        return '27-28'
#    elif age <= 32:
#        return '29-32'
#    elif age <= 38:
#        return '33-38'
#    else:
#        return '39+'

def get_location(longitude, latitude, provinces_json):
    
    point = Point(longitude, latitude)

    for record in provinces_json['features']:
        polygon = shape(record['geometry'])
        if polygon.contains(point):
            return record['properties']['name']
    return 'Binary error'

with open(data_path + 'rwanda_district.json') as data_file:    
        provinces_json = json.load(data_file)


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def get_data():
    status = pd.read_csv(data_path + 'status.csv')
    ev = pd.read_csv(data_path + 'events.csv')
    disaster = pd.read_csv(data_path + 'disasters.csv')

    df = status.merge(ev, how='left', on='event_id')
    df = df.merge(disaster, how='left', on='event_id')
    ####################################
    #Get n_samples records
    #df = df[df['longitude'] != 0].sample(n=n_samples)
    disasters_en = {'华为':'Huawei', '小米':'Xiaomi', '三星':'Samsung', 'vivo':'vivo', 'OPPO':'OPPO',
                        '魅族':'Meizu', '酷派':'Coolpad', '乐视':'LeEco', '联想':'Lenovo', 'HTC':'HTC'}

    df['disasters_en'] = df['disaster'].apply(lambda disaster: disaster_en[disaster] 
                                                    if (disaster in disasters_en) else 'Other')
    #df['age_segment'] = df['age'].apply(lambda age: get_age_segment(age))
    ##################################################

    df['location'] = df.apply(lambda row: get_location(row['longitude'], row['latitude'], provinces_json), axis=1)

    cols_to_keep = ['timestamp', 'longitude', 'latitude', 'disaster', 'status', 'location']
    df_clean = df[cols_to_keep].dropna()

    return df_clean.to_json(orient='records')


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)