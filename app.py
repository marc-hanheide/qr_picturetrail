#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template, request, send_file, session
from uuid import uuid4

from config import app_data

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes


@app.route("/")
def index():
    session.pop('found_ids', default=[])
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)

def initialise_session():
    for item in app_data["id_dict"]:
        found_id = 'found_'+item
        if found_id not in session:
            session[found_id] = False

@app.route("/trail")
def trail():
    id = request.args.get("id", default=0, type=str)
    if id in app_data["id_dict"]:
        initialise_session()
        found_id = 'found_'+id
        session[found_id] = True
        return render_template("trail.html", app_data=app_data, found=id)
    else:
        return render_template("trail.html", app_data=app_data, found=None)



@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)

@app.route("/qr/<id>")
def qr(id):
    import qrcode, io
    image = io.BytesIO()
    qrcode.make(app_data["base_url"] + "trail?id=" + id).save(image, "PNG")
    image.seek(0)
    return send_file(image, mimetype='image/png')


@app.route("/qrs")
def qrs():
    return render_template("qrs.html", app_data=app_data)




if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
