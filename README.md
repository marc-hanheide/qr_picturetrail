# qr_picturetrail
A simple web app for a picture trail

## Install

1. `python -m venv .venv`
1. `source .venv/bin/activate`
1. `pip install -r requirements.txt`

## Run

`python app.py`

### NGrok

To deploy publicly, use the ngrok command `ngrok1 -proto https -subdomain weltrail 5000` (only if you have your own ngrok server available and configured)