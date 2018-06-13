#!/usr/bin/python

from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, db

import json
import os

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
CERT_PATH = os.path.join(SITE_ROOT, 'rubrik-personalization-firebase-adminsdk-kua3q-a6416b2363.json')

application = Flask(__name__)
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


def process_get(request, rubrik_domain, user_name, component):
    json_url = os.path.join(SITE_ROOT, 'sample_get.json')
    return json.load(open(json_url))


@application.route("/personalization/<rubrik_domain>/<user_name>",
           methods=['POST'])
def handle_post(rubrik_domain, user_name):
    process_post(request, rubrik_domain, user_name)
    return 'OK'


@application.route("/personalization/<rubrik_domain>/<user_name>/<component>",
           methods=['GET'])
def handle_get(rubrik_domain, user_name, component):
    data = process_get(request, rubrik_domain, user_name, component)

    response = app.response_class(
        response=json.dumps(data),
        status=200,
        mimetype='application/json'
    )
    return response


# if __name__ == '__main__':
#     application.run()