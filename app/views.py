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

@app.route('/records', methods=['GET'])
def getRec():
    return jsonify({'records': records})

@app.route('/records', methods=['POST'])
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

@app.route('/records/<ttlName>', methods=['DELETE'])
def deleteTask(ttlName):
    matching = [item for item in records if item['title'] == ttlName]
    if len(matching) == 0:
        return make_response(jsonify({'-ERROR-': 'NOT FOUND'}), 404)
    records.remove(matching[0])
    return jsonify({'sucess', True})

@app.route('/records/<ttlName>', methods=['PUT'])
def updateTask(ttlName):
    matching = [item for item in records if item['title'] == ttlName]
    if len(matching) == 0:
        return make_response(jsonify({'-ERROR-': 'NOT FOUND'}), 404)
    if not request.json:
        return make_response(jsonify({'-ERROR-': 'FORMAT ERR'}), 400)
    matching[0]['title'] = request.json.get('title', matching[0]['title'])
    matching[0]['description'] = request.json.get('description', matching[0]['description'])
    matching[0]['done'] = request.json.get('done', matching[0]['done'])
    return jsonify({'task':matching[0]})

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'-ERROR-': 'NOT FOUND'}), 404)
