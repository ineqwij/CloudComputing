from app import app
from flask import Flask, jsonify

records = [
    {
        'id':1,
        'title':u'aaa',
        'descrption':u'bbb',
        'done':False
    },
    {
        'id':2,
        'title':u'ccc',
        'description':u'ddd',
        'done':True
    }
]

@app.route('/')
def index():
    return "<h1>----hello flask!----</h1>"

@app.route('/records/', methods=['GET'])
def getRec():
    return jsonify({'records': records})

@app.route('/records/alltasks', methods=['GET'])
def getTtl():
    response = [item['title'] for item in records]
    return jsonify(response)