from flask import Flask, render_template, request, jsonify, abort, redirect
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
import requests
from pprint import pprint
import requests_cache
from flask_pymongo import PyMongo

requests_cache.install_cache('air_api_cache', backend='sqlite', expire_after=36000)
app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'myDatabase'
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"
mongo = PyMongo(app)

air_url_template = 'https://api.breezometer.com/air-quality/v2/historical/hourly?lat={lat}&lon={lng}&key={API_KEY}&start_datetime={start}&end_datetime={end}'
MY_API_KEY = 'd6c882f5b3554498a8e88f04c7006fc8'

# @app.route('/downloaddata', methods=['GET'])
# def airchart():
#     my_latitude = request.args.get('lat','51.52369')
#     my_longitude = request.args.get('lng','-0.0395857')
#     my_start = request.args.get('start','2019-03-20T07:00:00Z')
#     my_end = request.args.get('end','2019-03-23T07:00:00Z')
#     air_url = air_url_template.format(lat=my_latitude, lng=my_longitude, API_KEY=MY_API_KEY, start=my_start, end=my_end)
#     resp = requests.get(air_url)
#     print(resp)
#     respJson = resp.json()['data']
#     #star = mongo.db.airData
#     # for item in respJson:
#     #     star_id = star.insert(item)
#     #     new_star = star.find_one({'_id': star_id})
#     #     print(item)
#     #pprint(resp)
#     if resp.ok:
#         resp = requests.get(air_url)
#         pprint(resp.json())
#         print(resp.json())
#     else:
#         print(resp.reason)
#     return "Done"

@app.route('/airqualitychart', methods=['GET'])
def airchart():
    my_latitude = request.args.get('lat','51.52369')
    my_longitude = request.args.get('lng','-0.0395857')
    my_start = request.args.get('start','2019-03-07T07:00:00Z')
    my_end = request.args.get('end','2019-03-09T07:00:00Z')
    air_url = air_url_template.format(lat=my_latitude, lng=my_longitude, API_KEY=MY_API_KEY, start=my_start, end=my_end)
    resp = requests.get(air_url)
    respJson = resp.json()['data']
    print(respJson)
    respJson = resp.json()['data']
    for item in respJson:
        sql = """INSERT INTO airqual.stats(DateTime, AQI, Category, Color, dName, DominantPollut) VALUES('{}', {}, '{}', '{}', '{}', '{}')""".format(str(item['datetime']), str(item['indexes']['baqi']['aqi']), str(item['indexes']['baqi']['category']),str(item['indexes']['baqi']['color']), str(item['indexes']['baqi']['display_name']),str(item['indexes']['baqi']['dominant_pollutant']))
        print(sql)
    if resp.ok:
        resp = requests.get(air_url)
        pprint(resp.json())
    else:
        print(resp.reason)
    return ("Done!")

@app.route('/list')
def list():
    tempData = mongo.db.airData.find({})
    print(tempData[0])
    data = []
    for i in tempData:
        data.append([i['datetime'], i['indexes']['baqi']['dominant_pollutant'], i['indexes']['baqi']['aqi_display']])
    return render_template('list.html', data = data)

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/index/del', methods=['DELETE'])
def delete():
    date = request.form.get('Date', None)
    mongo.db.airData.delete({'datetime':date})
    return redirect('/index')

@app.route('/index/add', methods=['POST'])
def add():
    date = request.form.get('cDate', None)
    aqi = request.form.get('cAqi', None)
    dominant_pollutant = request.form.get('cDP', None)
    mongo.db.airData.insert({'datetime': date, 'data_available': True, 'indexes': {'baqi': {'display_name': 'BreezoMeter AQI', 'aqi': int(aqi), 'aqi_display': aqi, 'color': '#C7E916', 'category': 'Moderate air quality', 'dominant_pollutant': dominant_pollutant}}})
    return redirect('/index')

@app.route('/index/upd', methods=['PUT'])
def upd():
    date = request.form.get('uDate', None)
    aqi = request.form.get('uAqi', None)
    dominant_pollutant = request.form.get('uDP', None)
    mongo.db.airData.update(
        {'datetime':date},
        {
            '$set':{
                'aqi':int(aqi),
                'aqi_display':aqi,
                'dominant_pollutant':dominant_pollutant
            }
        }
    )
    return redirect('/index')

@app.route('/')
def hello():
    return "<h1>HELLO HELLO</h1>"

if __name__=="__main__":
    app.run(port=8080, debug=True)