from flask import Flask, render_template, request, jsonify, abort, redirect
import requests
from pprint import pprint
import requests_cache
from cassandra.cluster import Cluster

requests_cache.install_cache('air_api_cache', backend='sqlite', expire_after=36000) # cache
cluster = Cluster(['cassandra'])
session = cluster.connect() # connect to cloud cluster of database
app = Flask(__name__)

air_url_template = 'https://api.breezometer.com/air-quality/v2/historical/hourly?lat={lat}&lon={lng}&key={API_KEY}&start_datetime={start}&end_datetime={end}'
MY_API_KEY = 'd6c882f5b3554498a8e88f04c7006fc8'

@app.route('/') # homepage, hello world
def hello():
    return('<h1>HELLO HELLO</h1>')

@app.route('/downloaddata', methods=['GET']) #get data from breezometer.com api
def airchart():
    my_latitude = request.args.get('lat','51.52369')
    my_longitude = request.args.get('lng','-0.0395857')
    my_start = request.args.get('start','2019-03-08T07:00:00Z')
    my_end = request.args.get('end','2019-03-10T07:00:00Z')
    air_url = air_url_template.format(lat=my_latitude, lng=my_longitude, API_KEY=MY_API_KEY, start=my_start, end=my_end)
    resp = requests.get(air_url)
    respJson = resp.json()['data']
    count = 0
    for item in respJson:
        sql = """INSERT INTO airqual.stats(DateTime, AQI, Category, Color, dName, DominantPollut) VALUES('{}', {}, '{}', '{}', '{}', '{}');""".format(str(item['datetime']), str(item['indexes']['baqi']['aqi']), str(item['indexes']['baqi']['category']), str(item['indexes']['baqi']['color']), str(item['indexes']['baqi']['display_name']), str(item['indexes']['baqi']['dominant_pollutant']))
        x = session.execute(sql)
        count += 1
        if count > 10:
            break
    if resp.ok:
        resp = requests.get(air_url)
        print(resp.json())
    else:
        print(resp.reason)
    return resp.json()

@app.route('/get') # return the json of data in database
def list():
    tempData = session.execute( 'Select * From airqual.stats')
    #print(tempData[0])
    count = 0
    result = {}
    for i in tempData:
        np = "data" + str(count)
        result[np] = i
        count += 1
    print(result)
    return jsonify({'record:':result})

@app.route('/index', methods=['GET']) #
def index():
    return render_template('index.html')

@app.route('/index/del/<date>') # delete one record of data in database
def delete(date):
    # date = request.form.get('Date', None)
    sql = """DELETE FROM airqual.stats WHERE DateTime='{}';""".format(str(date))
    x = session.execute(sql)
    return jsonify({'done':True})

@app.route('/index/add', methods=['POST']) # add one record of data to database
def add():
    date = request.form.get('cDate', None)
    aqi = request.form.get('cAqi', None)
    dominant_pollutant = request.form.get('cDP', None)
    sql = """INSERT INTO airqual.stats (DateTime, AQI, DominantPollut) VALUES ('"""+str(date)+"""',"""+str(aqi)+""",'"""+str(dominant_pollutant)+"""')"""
    x = session.execute(sql)
    # x = session.execute("""INSERT INTO airqual.stats(DateTime, AQI, DominantPollut) VALUES ('1234asd', 99, 'qwerty')""")
    return redirect('/index')

@app.route('/addone/') # add one record of data to database
def addOne():
    date = request.args.get('date','none')
    aqi = request.args.get('aqi', '0')
    dominant_pollutant = request.args.get('dp','none')
    sql = """INSERT INTO airqual.stats (DateTime, AQI, DominantPollut) VALUES ('"""+str(date)+"""',"""+str(aqi)+""",'"""+str(dominant_pollutant)+"""')"""
    x = session.execute(sql)
    # x = session.execute("""INSERT INTO airqual.stats(DateTime, AQI, DominantPollut) VALUES ('1234asd', 99, 'qwerty')""")
    return jsonify({'done':True})

@app.route('/index/getone')
def upd():
    date = request.form.get('uDate', None)
    aqi = request.form.get('uAqi', None)
    dominant_pollutant = request.form.get('uDP', None)
    sql = 'UPDATE airqual.stats SET AQI = %d WHERE DateTime = %s;'
    x = session.execute(sql, [int(aqi), str(date)])
    return redirect('/index')

if __name__=="__main__":
    app.run(host='0.0.0.0' , port=8080)