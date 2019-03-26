from flask import Flask, render_template, request, jsonify, abort, redirect
import requests
from pprint import pprint
import requests_cache
from cassandra.cluster import Cluster

requests_cache.install_cache('air_api_cache', backend='sqlite', expire_after=36000)
cluster = Cluster(['cassandra'])
session = cluster.connect()
app = Flask(__name__)

air_url_template = 'https://api.breezometer.com/air-quality/v2/historical/hourly?lat={lat}&lon={lng}&key={API_KEY}&start_datetime={start}&end_datetime={end}'
MY_API_KEY = 'd6c882f5b3554498a8e88f04c7006fc8'

@app.route('/')
def hello():
    return('<h1>HELLO HELLO</h1>')

@app.route('/downloaddata', methods=['GET'])
def airchart():
    my_latitude = request.args.get('lat','51.52369')
    my_longitude = request.args.get('lng','-0.0395857')
    my_start = request.args.get('start','2019-03-03T07:00:00Z')
    my_end = request.args.get('end','2019-03-07T07:00:00Z')
    air_url = air_url_template.format(lat=my_latitude, lng=my_longitude, API_KEY=MY_API_KEY, start=my_start, end=my_end)
    resp = requests.get(air_url)
    respJson = resp.json()['data']
    for item in respJson:
        sql = """INSERT INTO airqual.stats(DateTime, AQI, Category, Color, dName, DominantPollut) VALUES('{}', '{}', '{}', '{}', '{}', '{}')""".format(str(item['datetime']), str(item['indexes']['baqi']['aqi']), str(item['indexes']['baqi']['category']), str(item['indexes']['baqi']['color']), str(item['indexes']['baqi']['display_name']), str(item['indexes']['baqi']['dominant_pollutant']))
        x = session.execute(sql)
    #pprint(resp)
    if resp.ok:
        #resp = requests.get(air_url)
        pprint(resp.json())
    else:
        print(resp.reason)
    return "Done"

@app.route('/list')
def list():
    tempData = session.execute( 'Select * From airqual.stats')
    #print(tempData[0])
    data = []
    for i in tempData:
        data.append(str(i))
    return render_template('list.html', data = data)

@app.route('/index', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/index/del', methods=['DELETE'])
def delete():
    date = request.form.get('Date', None)
    sql = 'DELETE FROM airqual.stats WHERE DateTime=%s;'
    x = session.execute(sql, [str(date)])
    return redirect('/index')

@app.route('/index/add', methods=['POST'])
def add():
    date = request.form.get('cDate', None)
    aqi = request.form.get('cAqi', None)
    dominant_pollutant = request.form.get('cDP', None)
    sql = """INSERT INTO airqual.stats (DateTime, AQI, DominantPollut) VALUES ('"""+str(date)+"""',"""+str(aqi)+""",'"""+str(dominant_pollutant)+"""')"""
    x = session.execute(sql)
    # x = session.execute("""INSERT INTO airqual.stats(DateTime, AQI, DominantPollut) VALUES ('1234asd', 99, 'qwerty')""")
    return redirect('/index')

@app.route('/index/upd', methods=['PUT'])
def upd():
    date = request.form.get('uDate', None)
    aqi = request.form.get('uAqi', None)
    dominant_pollutant = request.form.get('uDP', None)
    sql = 'UPDATE airqual.stats SET AQI = %d WHERE DateTime = %s;'
    x = session.execute(sql, [int(aqi), str(date)])
    return redirect('/index')

if __name__=="__main__":
    app.run(host='0.0.0.0' , port=8080)