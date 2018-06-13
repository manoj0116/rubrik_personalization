#!/usr/bin/python

from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

import json
import os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
CERT_PATH = os.path.join(SITE_ROOT, 'rubrik-personalization-firebase-adminsdk-kua3q-a6416b2363.json')

app = Flask(__name__)
cred = credentials.Certificate(CERT_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://rubrik-personalization.firebaseio.com/'
})
root = db.reference()


def process_post(request, rubrik_domain, user_name):
    print "Processing post from domain: {} and user_name: {}" \
        .format(rubrik_domain, user_name)
    json = request.get_json()

    window = json["window"]
    track = json["track"]
    print "Window: {}".format(window)
    print "Track: {}".format(track)
    components = json["components"]
    for component in components:
        print "Component: {}".format(component)
        print components[component]


def process_get(request, rubrik_domain, user_name, component):
    print "Processing get from domain: {}, user_name: {} and component {}"\
        .format(rubrik_domain, user_name, component)
    json_url = os.path.join(SITE_ROOT, 'sample_get.json')
    return json.load(open(json_url))


@app.route("/personalization/<rubrik_domain>/<user_name>",
           methods=['POST'])
def handle_post(rubrik_domain, user_name):
    process_post(request, rubrik_domain, user_name)
    return 'OK'


@app.route("/personalization/<rubrik_domain>/<user_name>/<component>",
           methods=['GET'])
def handle_get(rubrik_domain, user_name, component):
    data = process_get(request, rubrik_domain, user_name, component)

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run()