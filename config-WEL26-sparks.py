app_data = {
    "name": "Bright Sparks of Lincolnshire",
    "data_consent": "By taking part, you agree that the photos you upload may be used by the West End Lights organisers to share and celebrate the event. Please only take photos of children with the permission of their parent or carer, and make sure everyone in the photo is happy to be included. Please do not include faces if you would prefer to stay private, a picture of hands, shadows or drawings works just as well!",
    "description": "Welcome to the Bright Sparks of Lincolnshire trail! Seven glowing posters are hidden around the West End. Each one tells the story of a bright spark with a link to Lincolnshire and to light: scientists, a castle defender, a glazier, an actor, a nurse and an explorer. Scan the QR code, discover their story and take a fun photo. Grown-ups, please help little explorers stay safe near roads.",
    "author": "Marc Hanheide",
    "html_title": "Bright Sparks of Lincolnshire",
    "project_name": "WEL 2026 Bright Sparks Trail",
    "keywords": "qr, trail, kids, children, light, history, lincolnshire, west end lights, lincoln, flask, webapp",
    "upload_folder": "static/uploads/",
    "theme": {
        "bg": "#0d1226",
        "accent": "#ffcf5c",
    },
    "map": {
        "style": "mapbox://styles/mapbox/dark-v11",
        "label_opacity": 0.45,
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
        "tiers": [
            {"max_distance": 20, "text": "✨ You're right there! Look around for the glowing {title} poster!", "highlight": "success", "vibrate": True},
            {"max_distance": 50, "text": "🔥 You're getting warmer! {title} is only {distance} away.", "highlight": "warning"},
            {"max_distance": 120, "text": "🚶 Nearly there! Keep going, {title} is close.", "highlight": "info"},
        ],
    },
    "id_dict": {
        # same location as "The Sun" in config-WEL26.py
        "6e26b9bb-7fc2-4fc2-9853-cbdd394328fb": {
            "image": "newton",
            "title": "Isaac Newton",
            "text": "Isaac Newton was born on Christmas Day 1642 at Woolsthorpe Manor, near Grantham in Lincolnshire. When he was a young man, he shone sunlight through a glass prism and discovered something amazing: white light is really made of all the colours of the rainbow!<br><br><b>Photo challenge:</b> Make a rainbow shape with your arms.<br>OR<br>Find something with lots of different colours and take a picture of it.",
            "hint": "Isaac was knighted by a Queen, so look for me in a street fit for royalty.",
            "lat": 53.236806,
            "lon": -0.549639,
            "near_text": "🌈 Can you see all the colours? Isaac Newton is right here!",
        },
        # same location as "Fire" in config-WEL26.py
        "15e6bc3d-70a2-40eb-b341-2f30ff68ded7": {
            "image": "ryall",
            "title": "Ann Ryall",
            "text": "Lincoln Cathedral has beautiful stained glass windows that turn sunlight into glowing, colourful pictures. In 1748 Ann Ryall took over her husband's job as the Cathedral's glazier and plumber. She is the first woman recorded doing this job at the Cathedral, and she kept it until 1752.<br><br><b>Photo challenge:</b> Find a window with coloured lights and take a picture.<br>OR<br>Make a window shape with your hands and peek through it.",
            "hint": "Where Ashlin meets Richmond.",
            "lat": 53.235194,
            "lon": -0.549472,
            "near_text": "🪟 Look for the colours! Ann Ryall's window is right here!",
        },
        # same location as "Light Bulb" in config-WEL26.py
        "2b1dd0f1-603d-42f0-b76d-3d5f99104c3c": {
            "image": "boole",
            "title": "George Boole",
            "text": "George Boole was born in Lincoln in 1815 and opened his own school here when he was only 19. He invented a kind of maths with just two answers: true or false, 1 or 0, ON or OFF. Today every computer, phone and LED light works using his idea! You can see his statue at Lincoln Central station.<br><br><b>Photo challenge:</b> Strike your brightest \"ON\" pose!<br>OR<br>Find a light that is switched on and take a picture of it.",
            "hint": "George was a teacher, so look for me near a (junior) school.",
            "lat": 53.234000,
            "lon": -0.551028,
            "near_text": "💡 Switch ON! George Boole is right here!",
        },
        # same location as "Fireflies" in config-WEL26.py
        "196e0aab-8c2e-4dd6-9a7a-7532669875b2": {
            "image": "swift",
            "title": "Sarah Swift",
            "text": "Sarah Swift was born in 1854 at Kirton Skeldyke, near Boston in Lincolnshire. She became a nurse, and in 1916 she helped start the College of Nursing, now the Royal College of Nursing, which still looks after nurses today. Long ago, nurses checked on their patients through the night by the light of a lamp.<br><br><b>Photo challenge:</b> Show us your kindest, most caring face.<br>OR<br>Give a teddy (or a grown-up) a pretend check-up.",
            "hint": "Caring is my thing! Find me near a place that offers wrap around care, with a breakfast club named after little glowing bugs.",
            "lat": 53.232472,
            "lon": -0.554194,
            "near_text": "🩺 You're very close! Sarah Swift is right here!",
        },
        # same location as "The Moon" in config-WEL26.py
        "7557db53-6af1-427c-bd95-870912d84257": {
            "image": "aldridge",
            "title": "Ira Aldridge",
            "text": "Ira Aldridge was a Black actor from New York who became a star of the stage in Britain and all across Europe. He was famous for playing Othello in Shakespeare's plays. He performed at the Theatre Royal in Lincoln in 1842 and 1849, when theatres were lit by flickering lamps.<br><br><b>Photo challenge:</b> Take a great big bow, as if you are in the spotlight!<br>OR<br>Show us your most dramatic acting face.",
            "hint": "Find me near a local cafe/restaurant in the <i>west</i> West-End.",
            "lat": 53.232139,
            "lon": -0.552722,
            "near_text": "🎭 Lights up! Ira Aldridge is on stage right here!",
        },
        # same location as "Lightning" in config-WEL26.py
        "dc4d4b4b-1eca-44ec-b273-40c3b663319d": {
            "image": "bungaree",
            "title": "Bungaree and Matthew Flinders",
            "text": "Matthew Flinders, born in Donington in Lincolnshire, sailed all the way round Australia in 1802 and 1803 to make a map of it. With him was Bungaree, an Aboriginal man from near Sydney, who helped the sailors talk with the people they met. He was the first known Aboriginal person to sail right round Australia! Sailors found their way using the sun and the stars. In 2024, Bungaree's family travelled from Australia to Donington to honour his old shipmate.<br><br><b>Photo challenge:</b> Point to the brightest star or light you can see.<br>OR<br>Row an imaginary boat across the ocean.",
            "hint": "Find me at a very COMMON entrance.",
            "lat": 53.232917,
            "lon": -0.550778,
            "near_text": "⭐ Ahoy! Bungaree and Matthew Flinders are right here!",
        },
        # same location as "LEDs" in config-WEL26.py
        "bbb65c95-be39-4eac-9563-d9fad84d9757": {
            "image": "nicholaa",
            "title": "Nicholaa de la Haye",
            "text": "More than 800 years ago, Nicholaa de la Haye looked after Lincoln Castle. In 1217, when she was in her sixties, enemy soldiers surrounded the castle, but she refused to give up! She held on until help arrived and the Battle of Lincoln was won. Like a guiding light, her castle showed the king's army where to come. King John even made her Sheriff of Lincolnshire.<br><br><b>Photo challenge:</b> Show us your bravest castle-guard pose.<br>OR<br>Make a castle tower with your arms (or with your friends).",
            "hint": 'I\'m where you can find horses during the day, and NOT where "Bungaree" is.',
            "lat": 53.233778,
            "lon": -0.548278,
            "near_text": "🏰 Stand guard! Nicholaa de la Haye is right here!",
        },
    },
}
