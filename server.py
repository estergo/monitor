from flask import Flask, send_file, json, Response, request, abort
from functools import wraps
from waitress import serve
import datetime
import time
import pymongo
from bson import json_util
import pandas as pd
from itertools import groupby
import os
import base64

app = Flask(__name__, static_folder='public')
connection_str = "mongodb://{}@{}".format(os.environ["MONGODB_SECRET"], os.environ["MONGODB_URI"])
# connection_str = 'mongodb://localhost:27017'
mongo_client = pymongo.MongoClient(connection_str)
db = mongo_client["statistics"]
db_col = db["monitor"]
customers = json.load(open('./data/customers.json'))

os.environ["AUTH"] = "bW9uaXRvci5mbXI6Rm1yMTIzNDU="

def authenticate(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.args.get('auth') or request.headers.get('Authorization') and request.headers.get('Authorization').split()[1]
        if not auth or not auth == os.environ["AUTH"]:
            return Response('Unauthorized', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
        return f(*args, **kwargs)
    return wrapper
    

@app.route('/')
@authenticate
def root():
    return app.send_static_file('index.html')

@app.route('/servers')
def get_servers():
    return send_file('./data/servers.json')

@app.route('/tests')
def get_tests():
    return send_file('./data/tests.json')

@app.route('/statistics')
def get_statistics():
    res = get_data()
    json_string = json.dumps(res, indent=4, default=json_util.default)
    return Response(json_string, content_type="application/json; charset=utf-8", status=200)

def get_data():

    crrent_time = datetime.datetime.now()   
    t1 = to_ms(crrent_time - datetime.timedelta(minutes=1))
    t5 = to_ms(crrent_time - datetime.timedelta(minutes=5))
    t30 = to_ms(crrent_time - datetime.timedelta(minutes=30))

    timestamps = [t30, t5, t1, to_ms(crrent_time)]
    titles = ['last30min', 'last5min', 'last1min']

    df = pd.DataFrame(list(db_col.find({'timestamp': {'$gte': t30}})))
    df['timestamp'] = pd.cut(df.timestamp, timestamps, labels=titles)

    success_df = df.loc[df['status'] == "200"]
    failed_df = df.loc[df['status'] != "200"]

    if not success_df.empty:
        statistics = success_df.groupby(["name", "server", "test", "timestamp"])["duration"].describe(percentiles=[.5, .9])
        count_err = failed_df.groupby(["name", "server", "test", "timestamp"])['status'].agg(['count']).rename(columns={"count": "failures"})
        final = pd.concat([statistics, count_err], axis=1)
        res = final.to_json(orient="index")
        # if not failed_df.empty:
        parsed = json.loads(res)
        return parsed
    else: 
        return []

def to_ms(t):
    return int(round(t.timestamp() * 1000))

@app.route('/details')
def get_details():
    params = request.args
    data = list(db_col.find({'name': params.get('customer'), 'server': params.get('server')}, {"test":1, "duration":1, "timestamp":1, "status":1, "_id": False}).sort('timestamp', pymongo.DESCENDING))
    for d in data:
        d['timestamp'] = datetime.datetime.fromtimestamp(d['timestamp']/1000.0)
    df = pd.DataFrame(data)
    html = df.to_html()
    return html

@app.route('/monitor', methods=['POST'])
@authenticate
def set_statistics():
    frm = request.form
    if not frm["customer"] or not frm["node"] or not frm["test"] or not frm["duration"] or not request.form["timestamp"] or not request.form["status"]:
        return Response('Missing data', 400)
    doc = {
        "name": customers[request.form["customer"]],
        "server": request.form["node"],
        "test": request.form["test"],
        "duration": float(request.form["duration"]),
        "timestamp": int(request.form["timestamp"]),
        "status": request.form["status"],
    }
    db_col.insert_one(doc)
    return "SUCCESS"

serve(app, host='0.0.0.0', port=5001)
