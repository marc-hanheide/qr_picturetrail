app_data = {
    "name": "West End Lights 2026 Picture Trail",
    "data_consent": "By taking part, you agree that the photos you upload may be used by the West End Lights organisers to share and celebrate the event. Please only take photos of children with the permission of their parent or carer, and make sure everyone in the photo is happy to be included. Please do not include faces if you would prefer to stay private, a picture of hands, shadows or drawings works just as well!",
    "description": "Welcome to the West End Lights trail! Find all the glowing posters hidden around the West End. At each one, scan the QR code, learn something new about light, and take a fun photo. Grown-ups, please help little explorers stay safe near roads.",
    "author": "Marc Hanheide",
    "html_title": "West End Lights 2026 Trail",
    "project_name": "WEL 2026 Picture Trail",
    "keywords": "qr, trail, kids, children, light, west end lights, lincoln, flask, webapp",
    "upload_folder": "static/uploads/",
    # optional, any key left out uses the default dark theme from app.py
    "theme": {
        "bg": "#0d1226",
        "accent": "#ffcf5c",
    },
    "map": {
        "style": "mapbox://styles/mapbox/dark-v11",
        "label_opacity": 0.45,  # dims street names so the map stays a backdrop
        "center": [-0.551236, 53.234472],  # [lon, lat]
        "zoom": 16.5,
        "bounds": [[-0.5565, 53.2312], [-0.5460, 53.2376]],  # [[west, south], [east, north]]
        "pitch": 0,
        "bearing": 0,
        "photo_size": 120,
        "stats_position": "right",
    },
    "proximity": {
        "update_interval_s": 5,
        "hysteresis_m": 8,
        "far_text": "{distance} away",
        # checked in order, first match wins; an item's "near_text" replaces the first tier's text
        "tiers": [
            {"max_distance": 20, "text": "✨ You're right there! Look around for the glowing {title} poster!", "highlight": "success", "vibrate": True},
            {"max_distance": 50, "text": "🔥 You're getting warmer! {title} is only {distance} away.", "highlight": "warning"},
            {"max_distance": 120, "text": "🚶 Nearly there! Keep going, {title} is close.", "highlight": "info"},
        ],
    },
    "id_dict": {
        "8b67f686-1fdb-4748-87a2-4ac3c4b9f8ce": {
            "image": "sun",
            "title": "The Sun",
            "text": "The sun is a giant ball of fire in space. It gives us light and keeps us warm!<br><br><b>Photo challenge:</b> Make the biggest, brightest sunshine smile you can!<br>OR<br>Stretch your arms out wide like sun rays.",
            "hint": "I'm the Queen of all lights, so I'm in a street named accordingly.",
            "lat": 53.236806,  # 53°14'12.5"N 0°32'58.7"W
            "lon": -0.549639,
            "near_text": "☀️ Can you feel the warmth? The Sun is shining right here!",
        },
        "93b49a5d-89f4-4eb5-85bb-cccb7db96901": {
            "image": "fire",
            "title": "Fire",
            "text": "When wood burns, it makes light and heat. A campfire keeps us cosy, but we always stay a safe distance away!<br><br><b>Photo challenge:</b> Pretend to warm your hands by a cosy campfire.<br>OR<br>Wiggle your fingers like dancing flames.",
            "hint": "Where Ashlin meets Richmond.",
            "lat": 53.235194,  # 53°14'06.7"N 0°32'58.1"W
            "lon": -0.549472,
        },
        "c30b1d2b-08e2-4567-abed-853f41bdd911": {
            "image": "lightbulb",
            "title": "Light Bulb",
            "text": "Inside an old light bulb is a tiny wire. When electricity flows through it, the wire gets so hot that it glows!<br><br><b>Photo challenge:</b> Show your \"I've got a bright idea!\" face, with one finger pointing up.<br>OR<br>Find a light that is switched on and take a picture of it.",
            "hint": "Shine a light on (junior) education!",
            "lat": 53.234000,  # 53°14'02.4"N 0°33'03.7"W
            "lon": -0.551028,
        },
        "2962bc7f-c4e2-4564-bb2d-054682254d4c": {
            "image": "fireflies",
            "title": "Fireflies",
            "text": "Fireflies are tiny bugs with their own lights inside their tummies. They blink to say hello to their friends!<br><br><b>Photo challenge:</b> Flap your arms and fly like a firefly.<br>OR<br>Blink your eyes and take a funny face photo.",
            "hint": "I can be found near a place that offers wrap around care and a breakfast club with my name.",
            "lat": 53.232472,  # 53°13'56.9"N 0°33'15.1"W
            "lon": -0.554194,
            "near_text": "✨ Blink, blink! The fireflies are buzzing all around you!",
        },
        "4f6add1e-44e4-40e2-967d-126f8ccfcb06": {
            "image": "moon",
            "title": "The Moon",
            "text": "The moon does not make its own light. It works like a big mirror and shines with light from the sun!<br><br><b>Photo challenge:</b> Make a moon shape with your arms over your head.<br>OR<br>Look up and take a picture of the sky. Can you spot the moon?",
            "hint": "Find me near a local cafe/restaurant in the <i>west</i> West-End.",
            "lat": 53.232139,  # 53°13'55.7"N 0°33'09.8"W
            "lon": -0.552722,
            "near_text": "🌙 Look up, look around! The Moon is right here!",
        },
        "c7c6f64d-d405-4349-8e23-c559ddf06632": {
            "image": "lightning",
            "title": "Lightning",
            "text": "Lightning is a giant spark in the sky during a storm. It is super bright and is followed by a loud BOOM of thunder!<br><br><b>Photo challenge:</b> Make a zig-zag lightning shape with your body.<br>OR<br>Show us your best surprised \"BOOM!\" face.",
            "hint": "Find me at a very COMMON entrance.",
            "lat": 53.232917,  # 53°13'58.5"N 0°33'02.8"W
            "lon": -0.550778,
            "near_text": "⚡ ZAP! Lightning has struck right next to you!",
        },
        "24e89728-f62d-4b5e-a1de-1b55e8c69610": {
            "image": "led",
            "title": "LEDs",
            "text": "LEDs are tiny lights used in TVs, toys and Christmas lights. They use very little electricity and last a long, long time!<br><br><b>Photo challenge:</b> Find some twinkly lights in a window and take a picture.<br>OR<br>Count how many colours of light you can see and show the number with your fingers.",
            "hint": 'I\'m where you can find horses during the day, and NOT where "lightning" is.',
            "lat": 53.233778,  # 53°14'01.6"N 0°32'53.8"W
            "lon": -0.548278,
        },
    },
}
