#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template, request, send_file, session, redirect
from uuid import uuid4
from csv import DictWriter
from datetime import datetime
from os import path

from config import app_data

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes

# if file exists open in append mode, if not create it

LOG_FILE='log.csv'

if path.exists('log.csv'):
    csv_file = open('log.csv', 'a')
    logwriter = DictWriter(csv_file, fieldnames=["id", "item", "session", "found", "ip", "user_agent", "referrer", "timestamp"])
else:
    csv_file = open('log.csv', 'w')
    logwriter = DictWriter(csv_file, fieldnames=["id", "item", "session", "found", "ip", "user_agent", "referrer", "timestamp"])
    logwriter.writeheader()

csv_file.flush()

@app.route("/")
def index():
    reset_session()
    return redirect("/trail", code=302)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)

def reset_session():
    for item in app_data["id_dict"]:
        found_id = 'found_'+item
        session[found_id] = False


def initialise_session():
    session.permanent = True
    app.permanent_session_lifetime = 3600
    if 'id' not in session:
        session['id'] = uuid4().hex
    for item in app_data["id_dict"]:
        found_id = 'found_'+item
        if found_id not in session:
            session[found_id] = False

@app.route("/trail")
def trail():
    id = request.args.get("id", default='', type=str)
    initialise_session()
    if id in app_data["id_dict"]:
        found_id = 'found_'+id
        session[found_id] = True
    items_found = 0
    for item in app_data["id_dict"]:
        if session['found_' + item] == True:
            items_found += 1
    items_total=len(app_data["id_dict"])
    if id in app_data["id_dict"]:
        try:
            logwriter.writerow({
                "id": id,
                "item": app_data["id_dict"][id]['image'],
                "session": session['id'],
                "found": items_found,
                "ip": request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0],
                "user_agent": request.user_agent.string,
                "referrer": request.referrer,
                "timestamp": datetime.now().isoformat()
            })
            csv_file.flush()
        except Exception as e:
            print("Could not write to log file %s" % e)
            #pass
    return render_template("trail.html", app_data=app_data, found=id, items_found=items_found, items_total=items_total)

def get_protocol(req):
    if req.headers.get('X-Forwarded-Proto') == 'https':
        return 'https'
    else:
        return 'http'

def get_base_url(req):
    return get_protocol(req) + '://' + req.headers.get('Host') + '/'

@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)

@app.route("/qr/<id>")
def qr(id):
    import qrcode, io
    image = io.BytesIO()
    qrcode.make(get_base_url(request) + "trail?id=" + id).save(image, "PNG")
    image.seek(0)
    return send_file(image, mimetype='image/png')

@app.route("/log")
def log():
    return send_file(LOG_FILE, mimetype='text/csv')


@app.route("/qrs")
def qrs():
    return render_template("qrs.html", app_data=app_data, base_url=get_base_url(request))


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV, port=5999, host='0.0.0.0')
