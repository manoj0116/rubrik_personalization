#!/usr/bin/python

from flask import Flask, request
import json
import os

app = Flask(__name__)

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))


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