#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template, request, send_file, session
from uuid import uuid4

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes

app_data = {
    "name": "QR Picture Trail",
    "base_url": "http://127.0.0.1:5000/",
    "description": "A basic Flask app using bootstrap to implement a QR-based picture trail.",
    "author": "Marc Hanheide",
    "html_title": "QR Picture Trail",
    "project_name": "QR_PictureTrail",
    "keywords": "qr, trail, kids, flask, webapp",
    "id_dict": {
        "9509af0a-1764-4095-aa5c-20726b654146": "lighthouse",
        "ce888ab1-ac19-40da-9b98-ebd65742d050": "lightning",
        "6e9ffaa0-688a-4a9e-8126-2d9c34596733": "lightbulb",
        "e29e6efd-4dcc-4fda-bebe-65657a66d6ad": "fireworks",
        "872055cd-4566-4403-a051-6fae3466f9d0": "candle",
        "d4b77f9b-446e-4898-982c-ca05109b2b3f": "torch",
        "18c5588a-11ce-4c74-88fd-1bbcf153f08f": "campfire",
        "250279a7-444e-4bed-9f7f-cd5d2eb8200d": "shootingstar"
    }
}


@app.route("/")
def index():
    session.pop('found_ids', default=[])
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


@app.route("/trail")
def trail():
    id = request.args.get("id", default=0, type=str)
    if 'found_ids' not in session:
        print('initialise')
        session['found_ids'] = []
    if id in app_data["id_dict"]:
        print('add ' + id + " to found_ids, which previously was:" + str(session['found_ids']))
        session['found_ids'].append(id)
        print(session['found_ids'])
        return render_template("trail.html", app_data=app_data, found=id, found_ids=session['found_ids'])
    else:
        return render_template("trail.html", app_data=app_data, found=None, found_ids=session['found_ids'])



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
