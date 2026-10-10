#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""
Peter Simeth's basic flask pretty youtube downloader (v1.3)
https://github.com/petersimeth/basic-flask-template
© MIT licensed, 2018-2023
"""

# Standard library imports
import re
import io
import html
import json
import os
import queue
import threading
import time
from collections import deque
from csv import DictWriter
from datetime import datetime, timezone
from os import path, listdir, makedirs
from uuid import uuid4

# Third-party imports
from flask import Flask, render_template, request, send_file, session, redirect, flash, url_for, make_response, Response, stream_with_context
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from PIL import Image
from dotenv import load_dotenv

import importlib.util

load_dotenv()


def load_app_data():
    """Load app_data from the file in TRAIL_CONFIG (default: config.py)."""
    config_path = os.environ.get('TRAIL_CONFIG', 'config.py')
    spec = importlib.util.spec_from_file_location('trail_config', config_path)
    if spec is None or not path.isfile(config_path):
        raise FileNotFoundError(f"Trail config file not found: {config_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(f"Loaded trail config from {config_path}")
    return module.app_data


app_data = load_app_data()


def generate_session_id():
    """Generate a human-readable session ID using coolname library (62+ billion combinations)."""
    from coolname import generate_slug
    return generate_slug(3)  # Generate 3-word slug like "ambitious-turaco-of-joviality"

DEVELOPMENT_ENV = True

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = uuid4().bytes

# Cookie serializer for secure admin authentication cookies
cookie_serializer = URLSafeTimedSerializer(app.secret_key)

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

LOG_FILE = os.environ.get('TRAIL_LOG_FILE', '/tmp/qrtrail.log') 

if path.exists(LOG_FILE):
    csv_file = open(LOG_FILE, "a")
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
    csv_file = open(LOG_FILE, "w")
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


def check_admin_access():
    """
    Check if the request has valid admin access token.
    Token can be provided as:
    - URL parameter: ?token=<token>
    - Authorization header: Authorization: Bearer <token>
    - Valid authentication cookie
    
    Returns tuple: (is_authenticated, token_provided_in_request)
    """
    admin_token = os.environ.get('TRAIL_ADMIN_ACCESS_TOKEN')
    
    if not admin_token:
        return False, False
    
    # Check for valid cookie first
    auth_cookie = request.cookies.get('admin_auth')
    if auth_cookie:
        try:
            # Verify cookie signature and check if it's not expired (4 weeks = 2419200 seconds)
            cookie_data = cookie_serializer.loads(auth_cookie, max_age=2419200)
            if cookie_data == admin_token:
                return True, False  # Authenticated via cookie, no token in request
        except (BadSignature, SignatureExpired):
            # Cookie is invalid or expired, continue to check other methods
            pass
    
    # Check URL parameter
    provided_token = request.args.get('token')
    if provided_token and provided_token == admin_token:
        return True, True  # Authenticated via token, token provided in request
    
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        bearer_token = auth_header.split(' ', 1)[1]
        if bearer_token == admin_token:
            return True, True  # Authenticated via header, token provided in request
    
    return False, False


def set_admin_auth_cookie(response):
    """
    Set a secure authentication cookie that's valid for 4 weeks.
    """
    admin_token = os.environ.get('TRAIL_ADMIN_ACCESS_TOKEN')
    if admin_token:
        # Create signed cookie with the admin token
        cookie_value = cookie_serializer.dumps(admin_token)
        
        # Set cookie for 4 weeks (2419200 seconds)
        response.set_cookie(
            'admin_auth',
            cookie_value,
            max_age=2419200,  # 4 weeks in seconds
            secure=request.is_secure,  # Only send over HTTPS in production
            httponly=True,  # Prevent JavaScript access
            samesite='Lax'  # CSRF protection
        )
    return response


def rescale_image(file_path, max_size=1024):
    """
    Rescale an image to fit within max_size x max_size while maintaining aspect ratio.
    
    Args:
        file_path (str): Path to the image file
        max_size (int): Maximum width or height in pixels
    """
    try:
        with Image.open(file_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            
            # Skip rescaling if image is already smaller than max_size
            if original_width <= max_size and original_height <= max_size:
                return
            
            # Calculate new dimensions while maintaining aspect ratio
            if original_width > original_height:
                # Landscape orientation
                new_width = max_size
                new_height = int((original_height * max_size) / original_width)
            else:
                # Portrait or square orientation
                new_height = max_size
                new_width = int((original_width * max_size) / original_height)
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save the resized image, preserving the original format
            # Convert RGBA to RGB if saving as JPEG
            if img.format == 'JPEG' or file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                if resized_img.mode == 'RGBA':
                    # Create a white background
                    background = Image.new('RGB', resized_img.size, (255, 255, 255))
                    background.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                    resized_img = background
                resized_img.save(file_path, 'JPEG', quality=90, optimize=True)
            else:
                resized_img.save(file_path, quality=90, optimize=True)
                
    except Exception as e:
        print(f"Error rescaling image {file_path}: {e}")
        # If rescaling fails, the original image remains unchanged


def generate_photo_filename(item_name, session_id, found_count):
    """Generate photo filename and ensure session directory exists."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
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
        'created': datetime.now(timezone.utc).isoformat(),
        'items_found': {},
        'photos': [],
        'total_found': 0,
        'last_updated': datetime.now(timezone.utc).isoformat()
    }


def save_session_data(session_id, session_data):
    """Save session data to trail.json file."""
    session_data['last_updated'] = datetime.now(timezone.utc).isoformat()
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
            'found_at': datetime.now(timezone.utc).isoformat(),
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
        'uploaded_at': datetime.now(timezone.utc).isoformat()
    }
    
    # Add to general photos list
    session_data['photos'].append(photo_info)
    
    # Add to specific item if it exists
    if item_id in session_data['items_found']:
        session_data['items_found'][item_id]['photos'].append(filename)
    
    save_session_data(session_id, session_data)
    return session_data


def upload_url(session_id, filename):
    """Public URL of an uploaded photo."""
    abs_path = path.abspath(path.join(app_data['upload_folder'], session_id, filename))
    # no url_for: also called at startup outside a request context
    return f"{app.static_url_path}/{path.relpath(abs_path, app.static_folder).replace(os.sep, '/')}"


class EventBroker:
    """Fan-out of server-sent events to all connected /map displays."""

    def __init__(self):
        self._subscribers = set()
        self._lock = threading.Lock()

    def subscribe(self):
        q = queue.Queue(maxsize=200)
        with self._lock:
            self._subscribers.add(q)
        return q

    def unsubscribe(self, q):
        with self._lock:
            self._subscribers.discard(q)

    def publish(self, event_type, data):
        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        with self._lock:
            subscribers = list(self._subscribers)
        for q in subscribers:
            try:
                q.put_nowait(message)
            except queue.Full:
                pass  # slow client, it resyncs via /map/state on reconnect


class StatsTracker:
    """In-memory engagement statistics, rebuilt from trail.json files at startup."""

    RECENT_WINDOW_S = 3600

    def __init__(self):
        self._lock = threading.Lock()
        self.reload()

    def reload(self):
        sessions = {}
        photos = 0
        latest_photos = {}
        recent = deque()
        last_activity = 0.0
        cutoff = time.time() - self.RECENT_WINDOW_S
        upload_folder = app_data['upload_folder']

        for session_id in (listdir(upload_folder) if path.isdir(upload_folder) else []):
            json_path = get_session_json_path(session_id)
            if not path.isfile(json_path):
                continue
            try:
                with open(json_path) as f:
                    data = json.load(f)
            except (json.JSONDecodeError, IOError):
                continue

            found = {i for i in data.get('items_found', {}) if i in app_data['id_dict']}
            if found:
                sessions[session_id] = found
            for item_id in found:
                ts = self._epoch(data['items_found'][item_id].get('found_at'))
                last_activity = max(last_activity, ts)
                if ts >= cutoff:
                    recent.append(ts)

            for photo in data.get('photos', []):
                item_id = photo.get('item_id')
                filename = photo.get('filename', '')
                if item_id not in app_data['id_dict'] or not path.isfile(path.join(upload_folder, session_id, filename)):
                    continue
                photos += 1
                ts = self._epoch(photo.get('uploaded_at'))
                last_activity = max(last_activity, ts)
                if item_id not in latest_photos or ts > latest_photos[item_id]['epoch']:
                    latest_photos[item_id] = {'url': upload_url(session_id, filename), 'ts': photo.get('uploaded_at'), 'epoch': ts}

        with self._lock:
            self._sessions = sessions
            self._photos = photos
            self._latest_photos = latest_photos
            self._recent = deque(sorted(recent))
            self._last_activity = last_activity or None

    @staticmethod
    def _epoch(iso_ts):
        try:
            return datetime.fromisoformat(iso_ts).timestamp()
        except (TypeError, ValueError):
            return 0.0

    def record_checkin(self, session_id, item_id):
        """Returns True if this session had not found this place before."""
        now = time.time()
        with self._lock:
            found = self._sessions.setdefault(session_id, set())
            self._last_activity = now
            if item_id in found:
                return False
            found.add(item_id)
            self._recent.append(now)
            return True

    def record_photo(self, item_id, url):
        now = time.time()
        ts = datetime.fromtimestamp(now, timezone.utc).isoformat()
        with self._lock:
            self._photos += 1
            self._last_activity = now
            self._latest_photos[item_id] = {'url': url, 'ts': ts, 'epoch': now}
        return {'item_id': item_id, 'url': url, 'ts': ts}

    def latest_photos(self):
        with self._lock:
            return {k: {'url': v['url'], 'ts': v['ts']} for k, v in self._latest_photos.items()}

    def snapshot(self):
        total_items = len(app_data['id_dict'])
        cutoff = time.time() - self.RECENT_WINDOW_S
        with self._lock:
            while self._recent and self._recent[0] < cutoff:
                self._recent.popleft()
            per_place = {item_id: 0 for item_id in app_data['id_dict']}
            for found in self._sessions.values():
                for item_id in found:
                    per_place[item_id] += 1
            return {
                'sessions': sum(1 for found in self._sessions.values() if found),
                'checkins': sum(per_place.values()),
                'completed': sum(1 for found in self._sessions.values() if len(found) >= total_items),
                'photos': self._photos,
                'total_places': total_items,
                'per_place': per_place,
                'recent_checkins': list(self._recent),
                'last_activity': self._last_activity,
            }


event_broker = EventBroker()
stats_tracker = StatsTracker()

DEFAULT_PROXIMITY = {
    "update_interval_s": 5,
    "hysteresis_m": 8,
    "far_text": "{distance} away",
    "tiers": [],
}


def get_proximity_config():
    return {**DEFAULT_PROXIMITY, **app_data.get("proximity", {})}


DEFAULT_THEME = {
    "bg": "#0d1226",
    "surface": "#171f3d",
    "surface_2": "#222c52",
    "text": "#f3f5fb",
    "muted": "#a4aecb",
    "accent": "#ffcf5c",
    "accent_text": "#2a1d00",
    "success": "#5ee09a",
    "info": "#7cc8ff",
    "danger": "#ff8080",
}


def get_theme():
    return {**DEFAULT_THEME, **app_data.get("theme", {})}


def get_session_photos(session_id):
    """Photo URLs of a session, grouped by item id, oldest first."""
    photos = {}
    for photo in load_session_data(session_id).get('photos', []):
        item_id, filename = photo.get('item_id'), photo.get('filename', '')
        if item_id in app_data['id_dict'] and path.isfile(path.join(app_data['upload_folder'], session_id, filename)):
            photos.setdefault(item_id, []).append(upload_url(session_id, filename))
    return photos


def get_map_places():
    """Places that have GPS coordinates, in id_dict order."""
    places = []
    for item_id, item in app_data['id_dict'].items():
        if 'lat' not in item or 'lon' not in item:
            continue
        icon = item['image'] + '.jpg'
        places.append({
            'id': item_id,
            'title': item['title'],
            'lat': item['lat'],
            'lon': item['lon'],
            'photo_side': item.get('photo_side', 'top'),
            'icon': url_for('static', filename=icon) if path.exists(path.join(app.static_folder, icon)) else None,
        })
    return places


@app.route("/")
def index():
    should_reset = request.args.get("reset", default=False, type=bool)
    if should_reset:
        reset_session()
    return redirect("/trail", code=302)


@app.route("/about")
def about():
    return render_template("about.html", app_data=app_data)


def reset_session():
    """Reset the current session by clearing all found items and generating a new session ID."""
    # Clear all found items
    for item in app_data["id_dict"]:
        found_id = "found_" + item
        session[found_id] = False
    
    session["consent_given"] = False
    # Clear the session ID to force generation of a new one
    if "id" in session:
        del session["id"]


def initialise_session():
    session.permanent = True
    app.permanent_session_lifetime = 24*3600
    if "id" not in session:
        session["id"] = generate_session_id()
    if "consent_given" not in session:
        session["consent_given"] = False
    for item in app_data["id_dict"]:
        found_id = "found_" + item
        if found_id not in session:
            session[found_id] = False


@app.route("/accept-consent", methods=['POST'])
def accept_consent():
    initialise_session()
    session["consent_given"] = True
    return {"success": True}, 200


@app.route("/trail", methods=['GET', 'POST'])
def trail():
    id = request.args.get("id", default="", type=str)
    initialise_session()
    
    # Handle photo upload
    if request.method == 'POST' and 'photo' in request.files:
        file = request.files['photo']
        item_id = request.form.get('item_id')
        wants_json = request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html
        
        if file and file.filename != '' and allowed_file(file.filename) and item_id in app_data["id_dict"]:
            # Count current found items
            items_found = sum(1 for item in app_data["id_dict"] if session["found_" + item])
            
            # Generate filename and session directory
            item_name = app_data["id_dict"][item_id]["image"]
            session_dir, filename = generate_photo_filename(item_name, session["id"], items_found)
            
            # Save file
            file_path = path.join(session_dir, filename)
            file.save(file_path)
            
            # Rescale the uploaded image to max 1024x1024 while maintaining aspect ratio
            rescale_image(file_path, max_size=1024)
            
            # Update session data with photo
            add_photo_to_session(session["id"], item_id, filename)
            event_broker.publish("photo", stats_tracker.record_photo(item_id, upload_url(session["id"], filename)))
            event_broker.publish("stats", stats_tracker.snapshot())
            # the redirect back to ?id= must not count as another check-in on the map
            session["just_uploaded"] = True
            
            if wants_json:
                return {"success": True}
            flash('Photo uploaded successfully!', 'success')
        else:
            if wants_json:
                return {"success": False, "message": "Invalid file or item."}, 400
            flash('Invalid file or item. Please try again.', 'error')
        
        return redirect(url_for('trail', id=item_id))
    
    just_uploaded = session.pop("just_uploaded", False)

    # Mark item as found if ID is provided
    if id in app_data["id_dict"]:
        found_id = "found_" + id
        session[found_id] = True
        
        # Update session data with found item
        item_name = app_data["id_dict"][id]["image"]
        update_session_with_item(session["id"], id, item_name)

        if not just_uploaded:
            is_new = stats_tracker.record_checkin(session["id"], id)
            event_broker.publish("checkin", {"item_id": id, "new": is_new})
            event_broker.publish("stats", stats_tracker.snapshot())
    
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
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )
            csv_file.flush()
        except Exception as e:
            print("Could not write to log file %s" % e)
            # pass
    
    return render_template(
        "trail.html",
        app_data=app_data,
        found=id if id in app_data["id_dict"] else "",
        items_found=items_found,
        items_total=items_total,
        proximity=get_proximity_config(),
        theme=get_theme(),
        photos_by_item=get_session_photos(session["id"]),
        just_uploaded=just_uploaded and id in app_data["id_dict"],
    )


def get_protocol(req):
    if req.headers.get("X-Forwarded-Proto") == "https":
        return "https"
    else:
        return "http"


def get_base_url(req):
    return get_protocol(req) + "://" + req.headers.get("Host") + "/"


def public_base_url(req):
    """Base URL encoded in QR codes; TRAIL_PUBLIC_URL wins so printing from localhost still works."""
    configured = os.environ.get("TRAIL_PUBLIC_URL", "").strip()
    return configured.rstrip("/") + "/" if configured else get_base_url(req)


def make_qr_image(url):
    import qrcode
    return qrcode.make(url, error_correction=qrcode.constants.ERROR_CORRECT_M, border=2).get_image().convert("RGB")


def poster_markup(text):
    """Escape config text for ReportLab paragraphs, keeping <b>, <i> and <br>."""
    text = html.escape(text or "", quote=False)
    text = re.sub(r"&lt;(/?)(b|i)&gt;", r"<\1\2>", text)
    return re.sub(r"&lt;br\s*/?&gt;", "<br/>", text)


def draw_qr_vector(pdf, url, x, y, size):
    """Vector QR code, sharp at any print size."""
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    cell = size / len(matrix)
    pdf.setFillColorRGB(0, 0, 0)
    for row, cells in enumerate(matrix):
        for col, dark in enumerate(cells):
            if dark:
                pdf.rect(x + col * cell, y + size - (row + 1) * cell, cell, cell, stroke=0, fill=1)


def build_posters_pdf(base_url):
    """One A4 poster per trail item, with a large QR code."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph

    width, height = A4
    margin = 15 * mm
    text_width = width - 2 * margin
    dark = colors.HexColor("#14182a")
    muted = colors.HexColor("#555b70")
    accent = colors.HexColor(get_theme()["accent"])
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=13.5, textColor=dark, alignment=TA_CENTER)
    item_style = ParagraphStyle("item", fontName="Helvetica", fontSize=12.5, leading=16, textColor=dark, alignment=TA_CENTER)
    small = ParagraphStyle("small", fontName="Helvetica", fontSize=7.5, leading=9.5, textColor=muted)
    total = len(app_data["id_dict"])

    how_to = Paragraph(
        f"<b>How to take part:</b> {poster_markup(app_data.get('description', ''))}<br/><br/>"
        f"<b>1.</b> Scan the QR code with your phone camera &#183; <b>2.</b> Find all {total} posters "
        f"&#183; <b>3.</b> Try the photo challenge (optional)",
        body,
    )
    consent = Paragraph(f"<b>Your photos &amp; privacy:</b> {poster_markup(app_data.get('data_consent', ''))}", small)
    _, how_h = how_to.wrap(text_width, height)
    _, consent_h = consent.wrap(text_width - 8 * mm, height)
    box_h = consent_h + 6 * mm
    how_y = margin + box_h + 5 * mm

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
    pdf.setTitle(f"{app_data['name']} posters")
    pdf.setAuthor(app_data.get("author", ""))

    for number, (item_id, item) in enumerate(app_data["id_dict"].items(), 1):
        url = base_url + "trail?id=" + item_id

        # top down: header, picture and the item's text
        pdf.setFillColor(accent)
        pdf.rect(0, height - 8 * mm, width, 8 * mm, stroke=0, fill=1)
        y = height - 19 * mm
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica-Bold", 15)
        pdf.drawCentredString(width / 2, y, app_data["name"])
        y -= 14 * mm
        pdf.setFillColor(dark)
        pdf.setFont("Helvetica-Bold", 36)
        pdf.drawCentredString(width / 2, y, item["title"])
        y -= 4 * mm

        image_path = path.join(app.static_folder, item["image"] + ".jpg")
        if path.isfile(image_path):
            image = ImageReader(image_path)
            image_w, image_h = image.getSize()
            draw_h = 30 * mm
            draw_w = min(image_w * draw_h / image_h, text_width)
            y -= draw_h
            pdf.drawImage(image, (width - draw_w) / 2, y, draw_w, draw_h, preserveAspectRatio=True, mask="auto")
            y -= 4 * mm

        item_text = Paragraph(poster_markup(item.get("text", "")), item_style)
        _, text_h = item_text.wrap(text_width, height)
        y -= text_h
        item_text.drawOn(pdf, margin, y)

        # bottom up: consent box and how to take part
        pdf.setStrokeColor(colors.HexColor("#c9cdd8"))
        pdf.roundRect(margin, margin, text_width, box_h, 3 * mm, stroke=1, fill=0)
        consent.drawOn(pdf, margin + 4 * mm, margin + 3 * mm)
        how_to.drawOn(pdf, margin, how_y)

        # the QR code fills the space in between, with its labels below it
        labels_h = 15 * mm
        space_top = y - 5 * mm
        space_bottom = how_y + how_h + 4 * mm
        qr_size = max(60 * mm, min(120 * mm, space_top - space_bottom - labels_h))
        qr_y = space_top - qr_size - max(0, (space_top - space_bottom - labels_h - qr_size) / 2)
        draw_qr_vector(pdf, url, (width - qr_size) / 2, qr_y, qr_size)
        pdf.setFillColor(dark)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(width / 2, qr_y - 7 * mm, "Scan me with your phone camera!")
        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(width / 2, qr_y - 12 * mm, url)

        pdf.setFillColor(muted)
        pdf.setFont("Helvetica", 8)
        pdf.drawRightString(width - margin, margin / 2, f"{number} / {total}")
        pdf.showPage()

    pdf.save()
    return buffer.getvalue()


@app.route("/contact")
def contact():
    return render_template("contact.html", app_data=app_data)


def qr_png(url):
    image = io.BytesIO()
    make_qr_image(url).save(image, "PNG")
    image.seek(0)
    return send_file(image, mimetype="image/png")


@app.route("/qr/<id>")
def qr(id):
    return qr_png(public_base_url(request) + "trail?id=" + id)


@app.route("/qr-join")
def qr_join():
    return qr_png(public_base_url(request) + "trail")


@app.route("/log")
def log():
    return send_file(LOG_FILE, mimetype="text/csv")


@app.route("/qrs")
def qrs():
    is_authenticated, token_provided = check_admin_access()
    
    if not is_authenticated:
        return "Access denied. Valid admin token required.", 403
    
    # If token was provided in the request, set cookie and redirect to clean URL
    if token_provided:
        response = make_response(redirect(url_for('qrs')))
        response = set_admin_auth_cookie(response)
        return response
    
    places = get_map_places()
    for place in places:
        place['qr'] = url_for('qr', id=place['id'])

    return render_template(
        "qrs.html",
        app_data=app_data,
        base_url=public_base_url(request),
        places=places,
        map_config=app_data.get("map", {}),
        mapbox_token=os.environ.get("MAPBOX_TOKEN", ""),
    )


@app.route("/qrs/posters.pdf")
def qr_posters_pdf():
    is_authenticated, _ = check_admin_access()
    if not is_authenticated:
        return "Access denied. Valid admin token required.", 403

    filename = re.sub(r"[^a-z0-9]+", "-", app_data["project_name"].lower()).strip("-") + "-posters.pdf"
    return send_file(
        io.BytesIO(build_posters_pdf(public_base_url(request))),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=filename,
    )


@app.route("/map")
def live_map():
    is_authenticated, token_provided = check_admin_access()

    if not is_authenticated:
        return "Access denied. Valid admin token required.", 403

    if token_provided:
        response = make_response(redirect(url_for('live_map')))
        return set_admin_auth_cookie(response)

    if "map" not in app_data or not get_map_places():
        return "Map not configured. Add a 'map' block and lat/lon for each place to the trail config.", 404

    return render_template(
        "map.html",
        app_data=app_data,
        map_config=app_data["map"],
        mapbox_token=os.environ.get("MAPBOX_TOKEN", ""),
        join_url=public_base_url(request) + "trail",
    )


@app.route("/map/state")
def map_state():
    is_authenticated, _ = check_admin_access()
    if not is_authenticated:
        return {"error": "Access denied."}, 403

    return {
        "places": get_map_places(),
        "photos": stats_tracker.latest_photos(),
        "stats": stats_tracker.snapshot(),
    }


@app.route("/map/events")
def map_events():
    is_authenticated, _ = check_admin_access()
    if not is_authenticated:
        return {"error": "Access denied."}, 403

    def stream():
        q = event_broker.subscribe()
        try:
            yield "retry: 3000\n\n"
            while True:
                try:
                    yield q.get(timeout=15)
                except queue.Empty:
                    yield ": keep-alive\n\n"
        finally:
            event_broker.unsubscribe(q)

    return Response(
        stream_with_context(stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.route("/gallery")
def gallery():
    is_authenticated, token_provided = check_admin_access()
    
    if not is_authenticated:
        return "Access denied. Valid admin token required.", 403
    
    # If token was provided in the request, set cookie and redirect to clean URL
    if token_provided:
        # Preserve page parameter in redirect
        page = request.args.get('page', 1, type=int)
        redirect_url = url_for('gallery', page=page) if page != 1 else url_for('gallery')
        response = make_response(redirect(redirect_url))
        response = set_admin_auth_cookie(response)
        return response
    
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
                    
                    most_recent = max(timestamps) if timestamps else datetime.now(timezone.utc)
                    
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
    
    # Sort sessions by photo count (primary) and total found items (secondary), both descending
    sessions.sort(key=lambda x: (x['photo_count'], x['total_found']), reverse=True)
    
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


@app.route("/delete-photo", methods=['POST'])
def delete_photo():
    """Delete a photo from a session."""
    is_authenticated, token_provided = check_admin_access()
    
    if not is_authenticated:
        return {"success": False, "message": "Access denied. Admin authentication required."}, 403
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        filename = data.get('filename')
        
        if not session_id or not filename:
            return {"success": False, "message": "Missing session_id or filename."}, 400
        
        # Validate filename to prevent path traversal attacks
        if '..' in filename or '/' in filename or '\\' in filename:
            return {"success": False, "message": "Invalid filename."}, 400
        
        # Get session directory and file path
        session_dir = path.join(app_data['upload_folder'], session_id)
        file_path = path.join(session_dir, filename)
        
        # Check if session directory exists
        if not path.exists(session_dir):
            return {"success": False, "message": "Session not found."}, 404
        
        # Check if file exists
        if not path.exists(file_path):
            return {"success": False, "message": "Photo not found."}, 404
        
        # Delete the file
        try:
            os.remove(file_path)
        except OSError as e:
            return {"success": False, "message": f"Failed to delete file: {str(e)}"}, 500
        
        # Update session data to remove photo reference
        session_data = load_session_data(session_id)
        
        # Remove from general photos list
        session_data['photos'] = [photo for photo in session_data.get('photos', []) 
                                  if photo.get('filename') != filename]
        
        # Remove from specific item photos
        for item_id, item_info in session_data.get('items_found', {}).items():
            if 'photos' in item_info:
                item_info['photos'] = [photo for photo in item_info['photos'] 
                                     if photo != filename]
        
        # Save updated session data
        save_session_data(session_id, session_data)
        stats_tracker.reload()
        event_broker.publish("reset", {})
        
        return {"success": True, "message": "Photo deleted successfully."}
        
    except Exception as e:
        print(f"Error deleting photo: {e}")
        return {"success": False, "message": "An unexpected error occurred."}, 500


@app.route("/delete-all-sessions", methods=['POST'])
def delete_all_sessions():
    """Delete all sessions and their associated photos."""
    is_authenticated, token_provided = check_admin_access()
    
    if not is_authenticated:
        return {"success": False, "message": "Access denied. Admin authentication required."}, 403
    
    try:
        upload_folder = app_data['upload_folder']
        
        if not path.exists(upload_folder):
            return {"success": True, "message": "No sessions to delete."}
        
        deleted_sessions = 0
        deleted_files = 0
        
        # Get all session directories
        for item in listdir(upload_folder):
            session_path = path.join(upload_folder, item)
            
            if path.isdir(session_path):
                try:
                    # Count files before deletion
                    files_in_session = 0
                    for file_item in listdir(session_path):
                        file_path = path.join(session_path, file_item)
                        if path.isfile(file_path):
                            try:
                                os.remove(file_path)
                                files_in_session += 1
                            except OSError as e:
                                print(f"Error deleting file {file_path}: {e}")
                    
                    # Remove the session directory
                    try:
                        os.rmdir(session_path)
                        deleted_sessions += 1
                        deleted_files += files_in_session
                    except OSError as e:
                        print(f"Error removing directory {session_path}: {e}")
                        
                except OSError as e:
                    print(f"Error processing session directory {session_path}: {e}")
                    continue

        stats_tracker.reload()
        event_broker.publish("reset", {})
        
        return {
            "success": True, 
            "message": f"Successfully deleted {deleted_sessions} session(s) and {deleted_files} file(s).",
            "deleted_sessions": deleted_sessions,
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        print(f"Error deleting all sessions: {e}")
        return {"success": False, "message": "An unexpected error occurred during bulk deletion."}, 500


if __name__ == "__main__":
    app.run(debug=DEVELOPMENT_ENV, port=5999, host="0.0.0.0")
