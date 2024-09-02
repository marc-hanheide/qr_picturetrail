#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template, request

DEVELOPMENT_ENV = True

app = Flask(__name__)

app_data = {
    "name": "QR Picture Trail",
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
    return render_template("index.html", app_data=app_data)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


@app.route("/trail")
def trail():
    id = request.args.get("id", default=0, type=str)
    if id in app_data["id_dict"]:
        return render_template("trail.html", app_data=app_data, found=id)
    else:
        return render_template("trail.html", app_data=app_data, found=None)



@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV)
