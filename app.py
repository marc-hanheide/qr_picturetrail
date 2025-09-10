#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

from flask import Flask, render_template, request, send_file, session, redirect, flash, url_for
from uuid import uuid4
from csv import DictWriter
from datetime import datetime
from os import path, listdir, makedirs
from werkzeug.utils import secure_filename
import re
import glob

from config import app_data

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes

# Configure upload settings
app.config['UPLOAD_FOLDER'] = app_data['upload_folder']
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Create upload directory if it doesn't exist
makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# if file exists open in append mode, if not create it

LOG_FILE = "log.csv"

if path.exists("log.csv"):
    csv_file = open("log.csv", "a")
    logwriter = DictWriter(
        csv_file,
        fieldnames=[
            "id",
            "item",
            "session",
            "found",
            "ip",
            "user_agent",
            "referrer",
            "timestamp",
        ],
    )
else:
    csv_file = open("log.csv", "w")
    logwriter = DictWriter(
        csv_file,
        fieldnames=[
            "id",
            "item",
            "session",
            "found",
            "ip",
            "user_agent",
            "referrer",
            "timestamp",
        ],
    )
    logwriter.writeheader()

csv_file.flush()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_photo_filename(item_name, session_id, found_count):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{item_name}_{timestamp}_{session_id}_{found_count}.jpg"


@app.route("/")
def index():
    reset_session()
    return redirect("/trail", code=302)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


def reset_session():
    for item in app_data["id_dict"]:
        found_id = "found_" + item
        session[found_id] = False


def initialise_session():
    session.permanent = True
    app.permanent_session_lifetime = 3600
    if "id" not in session:
        session["id"] = uuid4().hex
    for item in app_data["id_dict"]:
        found_id = "found_" + item
        if found_id not in session:
            session[found_id] = False


@app.route("/trail", methods=['GET', 'POST'])
def trail():
    id = request.args.get("id", default="", type=str)
    initialise_session()
    
    # Handle photo upload
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        item_id = request.form.get('item_id')
        
        if file and file.filename != '' and allowed_file(file.filename) and item_id in app_data["id_dict"]:
            # Count current found items
            items_found = sum(1 for item in app_data["id_dict"] if session["found_" + item])
            
            # Generate filename
            item_name = app_data["id_dict"][item_id]["image"]
            filename = generate_photo_filename(item_name, session["id"], items_found)
            
            # Save file
            file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            flash('Photo uploaded successfully!', 'success')
        else:
            flash('Invalid file or item. Please try again.', 'error')
        
        return redirect(url_for('trail', id=item_id))
    
    # Mark item as found if ID is provided
    if id in app_data["id_dict"]:
        found_id = "found_" + id
        session[found_id] = True
    
    items_found = 0
    for item in app_data["id_dict"]:
        if session["found_" + item] == True:
            items_found += 1
    items_total = len(app_data["id_dict"])
    
    if id in app_data["id_dict"]:
        try:
            logwriter.writerow(
                {
                    "id": id,
                    "item": app_data["id_dict"][id]["image"],
                    "session": session["id"],
                    "found": items_found,
                    "ip": request.headers.get(
                        "X-Forwarded-For", request.remote_addr
                    ).split(",")[0],
                    "user_agent": request.user_agent.string,
                    "referrer": request.referrer,
                    "timestamp": datetime.now().isoformat(),
                }
            )
            csv_file.flush()
        except Exception as e:
            print("Could not write to log file %s" % e)
            # pass
    
    return render_template(
        "trail.html",
        app_data=app_data,
        found=id,
        items_found=items_found,
        items_total=items_total,
    )


def get_protocol(req):
    if req.headers.get("X-Forwarded-Proto") == "https":
        return "https"
    else:
        return "http"


def get_base_url(req):
    return get_protocol(req) + "://" + req.headers.get("Host") + "/"


@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


@app.route("/qr/<id>")
def qr(id):
    import qrcode, io

    image = io.BytesIO()
    qrcode.make(get_base_url(request) + "trail?id=" + id).save(image, "PNG")
    image.seek(0)
    return send_file(image, mimetype="image/png")


@app.route("/log")
def log():
    return send_file(LOG_FILE, mimetype="text/csv")


@app.route("/qrs")
def qrs():
    return render_template(
        "qrs.html", app_data=app_data, base_url=get_base_url(request)
    )


def parse_photo_filename(filename):
    """Parse photo filename to extract metadata."""
    # Expected format: itemname_YYYYMMDD_HHMMSS_sessionid_foundcount.jpg
    pattern = r'^(.+?)_(\d{8}_\d{6})_([^_]+)_(\d+)\.(jpg|jpeg|png|gif)$'
    match = re.match(pattern, filename)
    
    if match:
        item_name, timestamp_str, session_id, found_count, ext = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            return {
                'filename': filename,
                'item_name': item_name,
                'timestamp': timestamp,
                'session_id': session_id,
                'found_count': int(found_count),
                'extension': ext
            }
        except ValueError:
            return None
    return None


@app.route("/gallery")
def gallery():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    # Get all photos from upload folder
    upload_folder = app.config['UPLOAD_FOLDER']
    photo_files = []
    
    if path.exists(upload_folder):
        for filename in listdir(upload_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                photo_data = parse_photo_filename(filename)
                if photo_data:
                    photo_files.append(photo_data)
    
    # Group photos by session
    sessions = {}
    for photo in photo_files:
        session_id = photo['session_id']
        if session_id not in sessions:
            sessions[session_id] = []
        sessions[session_id].append(photo)
    
    # Sort photos within each session by timestamp (most recent first)
    for session_id in sessions:
        sessions[session_id].sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Sort sessions by the timestamp of their most recent photo
    sorted_sessions = []
    for session_id, photos in sessions.items():
        most_recent_timestamp = max(photo['timestamp'] for photo in photos)
        sorted_sessions.append({
            'session_id': session_id,
            'photos': photos,
            'most_recent': most_recent_timestamp,
            'photo_count': len(photos)
        })
    
    sorted_sessions.sort(key=lambda x: x['most_recent'], reverse=True)
    
    # Implement pagination
    total_sessions = len(sorted_sessions)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_sessions = sorted_sessions[start:end]
    
    # Calculate pagination info
    has_prev = page > 1
    has_next = end < total_sessions
    prev_num = page - 1 if has_prev else None
    next_num = page + 1 if has_next else None
    
    return render_template(
        "gallery.html",
        app_data=app_data,
        sessions=paginated_sessions,
        page=page,
        per_page=per_page,
        total_sessions=total_sessions,
        has_prev=has_prev,
        has_next=has_next,
        prev_num=prev_num,
        next_num=next_num
    )


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV, port=5999, host="0.0.0.0")
