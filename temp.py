from flask import Flask, request
from cassandra.cluster import Cluster
cluster = Cluster(['cassandra'])
session = cluster.connect()
app = Flask(__name__)
@app.route('/')
def hello():
    name = request.args.get("name","World")
    return('<h1>Hello, {}!</h1>'.format(name))
@app.route('/pokemon/<name>')
def profile(name):
    rows = session.execute( """Select * From pokemon.stats where name = '{}'""".format(name))
    for pokemon in rows:
        return('<h1>{} has {} attack!</h1>'.format(name,pokemon.attack))
    return('<h1>That Pokemon does not exist!</h1>')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
