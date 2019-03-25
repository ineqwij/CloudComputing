from app import app
from flask import Flask, jsonify, make_response, request

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

@app.route('/records/', methods=['POST'])
def createRec():
    if not request.json or not 'title' in request.json:
        return make_response(jsonify({'-ERROR-': 'NEED TITLE'}), 400)
    task = {
        'id':records[-1]['id'] + 1,
        'title':request.json['title'],
        'description': request.json.get('description', ""),
        'done':False
    }
    records.append(task)
    return jsonify({'records': task}), 201

@app.route('/records/alltasks', methods=['GET'])
def getTtl():
    response = [item['title'] for item in records]
    return jsonify(response)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'-ERROR-': 'NOT FOUND'}), 404)
