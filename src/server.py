#!/usr/bin/python

from flask import Flask, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

import json
import os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
CERT_PATH = os.path.join(SITE_ROOT, 'rubrik-personalization-firebase-adminsdk-kua3q-a6416b2363.json')

application = Flask(__name__)
CORS(application)
cred = credentials.Certificate(CERT_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://rubrik-personalization.firebaseio.com/'
})
root = db.reference()


def process_post(request, rubrik_domain, user_name):
    json = request.get_json()

    if not key_exists(root, rubrik_domain):
        root.update({
            rubrik_domain: {
                user_name: json["components"]
            }
        })
        return

    domain = root.child(rubrik_domain)

    if not key_exists(domain, user_name):
        domain.update({
            user_name: json["components"]
        })
        return

    user = domain.child(user_name)

    for component_name, component_value in json["components"].items():
        if not key_exists(user, component_name):
            user.update({
                component_name: component_value
            })
        else:
            component = user.child(component_name)
            for item_name, item_value in component_value.items():
                if not key_exists(component, item_name):
                    component.update({
                        item_name: item_value
                    })
                else:
                    item = component.child(item_name)
                    item.set(item.get() + item_value)

def key_exists(root, key):
    data = root.get(shallow=True)
    try:
        data[key]
        return True
    except KeyError as e:
        return False


def process_get(request, rubrik_domain, user_name, component_name):
    if key_exists(root, rubrik_domain):
        domain = root.child(rubrik_domain)
        if key_exists(domain, user_name):
            user = domain.child(user_name)
            if key_exists(user, component_name):
                component = user.child(component_name).get()
                return [v[0] for v in sorted(component.items(),
                                             key=lambda kv: (kv[1], kv[0]),
                                             reverse=True)]
    return []


@application.route("/personalization/<rubrik_domain>/<user_name>",
           methods=['POST'])
def handle_post(rubrik_domain, user_name):
    process_post(request, rubrik_domain, user_name)
    return 'OK'


@application.route("/personalization/<rubrik_domain>/<user_name>/<component>",
           methods=['GET'])
def handle_get(rubrik_domain, user_name, component):
    data = process_get(request, rubrik_domain, user_name, component)

    response = application.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    application.run()