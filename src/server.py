#!/usr/bin/python

from flask import Flask, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

import json
import math
import os
import time

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
    rubrik_domain = firebase_format(rubrik_domain)
    user_name = firebase_format(user_name)

    json = request.get_json()

    if not key_exists(root, rubrik_domain):
        root.update({
            rubrik_domain: {
                user_name: json["components"]
            }
        })
    else:
        domain = root.child(rubrik_domain)

        if not key_exists(domain, user_name):
            domain.update({
                user_name: json["components"]
            })
        else:
            user = domain.child(user_name)

            for component_name, component_value in json["components"].items():
                if not key_exists(user, component_name):
                    user.update({
                        component_name: component_value
                    })

    domain = root.child(rubrik_domain)
    user = domain.child(user_name)
    current_ts = time.time()
    for component_name, component_value in json["components"].items():
        component = user.child(component_name)
        links = component.child("links")
        for item_name, item_value in component_value["links"].items():
            item = links.child(item_name)
            item.update({
                "ts": current_ts
            })

        if key_exists(component, "comp_ts"):
            old_ts = float(component.child("comp_ts").get())
            links = component.child("links")
            for item_name, item_value in links.get().items():
                item = links.child(item_name)

                new_count = 0
                try:
                    new_count = component_value["links"][item_name]["count"]
                except KeyError as e:
                    pass

                if key_exists(item, "count"):
                    old_count = float(item.child("count").get())
                else:
                    old_count = 0

                item.child("count").set((old_count * max(0, (float(1) - float(
                    current_ts - old_ts) / float(86400)))) + new_count)

        component.update({
            "comp_ts": current_ts
        })


def key_exists(root, key):
    data = root.get(shallow=True)
    try:
        data[key]
        return True
    except KeyError as e:
        return False


def process_get(request, rubrik_domain, user_name, component_name):
    rubrik_domain = firebase_format(rubrik_domain)
    user_name = firebase_format(user_name)
    if key_exists(root, rubrik_domain):
        domain = root.child(rubrik_domain)
        if key_exists(domain, user_name):
            user = domain.child(user_name)
            if key_exists(user, component_name):
                component = user.child(component_name)
                links = component.child("links")
                dict = {}
                for link_name, link_value in links.get().items():
                    dict[link_name] = link_value["count"]
                return [v[0] for v in sorted(dict.items(),
                                             key=lambda kv: (kv[1], kv[0]),
                                             reverse=True)]
    return []


def firebase_format(str):
    return str.replace(".", "_")


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