#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

# Standard library imports
import re
import json
from csv import DictWriter
from datetime import datetime
from os import path, listdir, makedirs
from uuid import uuid4

# Third-party imports
from flask import Flask, render_template, request, send_file, session, redirect, flash, url_for

# Local imports
from config import app_data


def generate_session_id():
    """Generate a human-readable session ID using coolname library (62+ billion combinations)."""
    from coolname import generate_slug
    return generate_slug(3)  # Generate 3-word slug like "ambitious-turaco-of-joviality"

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes

# Add custom filter to check if file exists
@app.template_filter('file_exists')
def file_exists(filepath):
    """Check if a file exists in the static folder"""
    full_path = path.join(app.static_folder, filepath)
    return path.exists(full_path)

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
    """Generate photo filename and ensure session directory exists."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{item_name}_{timestamp}_{found_count}.jpg"
    
    # Create session directory path
    session_dir = path.join(app_data['upload_folder'], session_id)
    makedirs(session_dir, exist_ok=True)
    
    return session_dir, filename


def get_session_json_path(session_id):
    """Get the path to the trail.json file for a session."""
    session_dir = path.join(app_data['upload_folder'], session_id)
    return path.join(session_dir, 'trail.json')


def load_session_data(session_id):
    """Load session data from trail.json file."""
    json_path = get_session_json_path(session_id)
    if path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    
    # Return default session data if file doesn't exist or is corrupted
    return {
        'session_id': session_id,
        'created': datetime.now().isoformat(),
        'items_found': {},
        'photos': [],
        'total_found': 0,
        'last_updated': datetime.now().isoformat()
    }


def save_session_data(session_id, session_data):
    """Save session data to trail.json file."""
    session_data['last_updated'] = datetime.now().isoformat()
    json_path = get_session_json_path(session_id)
    
    # Ensure directory exists
    session_dir = path.dirname(json_path)
    makedirs(session_dir, exist_ok=True)
    
    try:
        with open(json_path, 'w') as f:
            json.dump(session_data, f, indent=2)
    except IOError as e:
        print(f"Could not save session data: {e}")


def update_session_with_item(session_id, item_id, item_name):
    """Update session data when an item is found."""
    session_data = load_session_data(session_id)
    
    if item_id not in session_data['items_found']:
        session_data['items_found'][item_id] = {
            'name': item_name,
            'found_at': datetime.now().isoformat(),
            'photos': []
        }
        session_data['total_found'] = len(session_data['items_found'])
    
    save_session_data(session_id, session_data)
    return session_data


def add_photo_to_session(session_id, item_id, filename):
    """Add a photo record to the session data."""
    session_data = load_session_data(session_id)
    
    photo_info = {
        'filename': filename,
        'item_id': item_id,
        'uploaded_at': datetime.now().isoformat()
    }
    
    # Add to general photos list
    session_data['photos'].append(photo_info)
    
    # Add to specific item if it exists
    if item_id in session_data['items_found']:
        session_data['items_found'][item_id]['photos'].append(filename)
    
    save_session_data(session_id, session_data)
    return session_data


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
        session["id"] = generate_session_id()
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
            
            # Generate filename and session directory
            item_name = app_data["id_dict"][item_id]["image"]
            session_dir, filename = generate_photo_filename(item_name, session["id"], items_found)
            
            # Save file
            file_path = path.join(session_dir, filename)
            file.save(file_path)
            
            # Update session data with photo
            add_photo_to_session(session["id"], item_id, filename)
            
            flash('Photo uploaded successfully!', 'success')
        else:
            flash('Invalid file or item. Please try again.', 'error')
        
        return redirect(url_for('trail', id=item_id))
    
    # Mark item as found if ID is provided
    if id in app_data["id_dict"]:
        found_id = "found_" + id
        session[found_id] = True
        
        # Update session data with found item
        item_name = app_data["id_dict"][id]["image"]
        update_session_with_item(session["id"], id, item_name)
    
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


@app.route("/gallery")
def gallery():
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    upload_folder = app.config['UPLOAD_FOLDER']
    sessions = []
    
    if path.exists(upload_folder):
        # Get all session directories
        for item in listdir(upload_folder):
            session_path = path.join(upload_folder, item)
            if path.isdir(session_path):
                session_data = load_session_data(item)
                
                # Get photo files in session directory
                photo_files = []
                for filename in listdir(session_path):
                    if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                        photo_path = path.join(session_path, filename)
                        if path.isfile(photo_path):
                            # Get file timestamp as fallback
                            file_stat = path.getmtime(photo_path)
                            file_timestamp = datetime.fromtimestamp(file_stat)
                            
                            # Try to find photo info in session data
                            photo_info = None
                            for photo in session_data.get('photos', []):
                                if photo['filename'] == filename:
                                    photo_info = photo
                                    break
                            
                            # Find item name for this photo
                            item_name = 'unknown'
                            if photo_info and photo_info.get('item_id'):
                                item_id = photo_info['item_id']
                                if item_id in app_data['id_dict']:
                                    item_name = app_data['id_dict'][item_id]['image']
                                elif item_id in session_data.get('items_found', {}):
                                    item_name = session_data['items_found'][item_id]['name']
                            else:
                                # Try to extract from filename as fallback
                                name_part = filename.split('_')[0] if '_' in filename else filename.split('.')[0]
                                item_name = name_part
                            
                            photo_data = {
                                'filename': filename,
                                'item_name': item_name,
                                'timestamp': datetime.fromisoformat(photo_info['uploaded_at']) if photo_info else file_timestamp,
                                'session_id': item,
                                'found_count': session_data.get('total_found', 0),
                                'session_path': item  # For constructing image URLs
                            }
                            photo_files.append(photo_data)
                
                if photo_files or session_data.get('items_found'):
                    # Sort photos by timestamp (most recent first)
                    photo_files.sort(key=lambda x: x['timestamp'], reverse=True)
                    
                    # Get most recent activity timestamp
                    timestamps = []
                    if photo_files:
                        timestamps.extend([photo['timestamp'] for photo in photo_files])
                    
                    # Add item found timestamps
                    for item_info in session_data.get('items_found', {}).values():
                        if 'found_at' in item_info:
                            timestamps.append(datetime.fromisoformat(item_info['found_at']))
                    
                    # Add session creation time
                    if 'created' in session_data:
                        timestamps.append(datetime.fromisoformat(session_data['created']))
                    
                    most_recent = max(timestamps) if timestamps else datetime.now()
                    
                    session_info = {
                        'session_id': item,
                        'photos': photo_files,
                        'most_recent': most_recent,
                        'photo_count': len(photo_files),
                        'total_found': session_data.get('total_found', 0),
                        'items_found': session_data.get('items_found', {}),
                        'created': datetime.fromisoformat(session_data['created']) if 'created' in session_data else most_recent
                    }
                    sessions.append(session_info)
    
    # Sort sessions by most recent activity
    sessions.sort(key=lambda x: x['most_recent'], reverse=True)
    
    # Implement pagination
    total_sessions = len(sessions)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_sessions = sessions[start:end]
    
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
