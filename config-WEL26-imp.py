JUNIOR_CREDIT = "<br><br><i>Drawn by a pupil at St Faith and St Martin Junior School</i>"
INFANT_CREDIT = "<br><br><i>Drawn by a child at St Faith's Infant and Nursery School</i>"


def imp_text(comment, fact, challenge, alternative, credit):
    return (
        f"{comment}"
        f"<br><br><b>Secret Imp fact:</b> {fact}"
        f"<br><br><b>Photo challenge:</b> {challenge}<br>OR<br>{alternative}"
        f"{credit}"
    )


app_data = {
    "name": "West End Lights 2026: The Imp's Night-Time Gallery",
    "data_consent": "By taking part, you agree that the photos you upload may be used by the West End Lights organisers to share and celebrate the event. Please only take photos of children with the permission of their parent or carer, and make sure everyone in the photo is happy to be included. Please do not include faces if you would prefer to stay private, a picture of hands, shadows or drawings works just as well!",
    "description": "Psst! It's me, the Lincoln Imp! I've crept out of the Cathedral for West End Lights, and I've hidden 11 amazing pictures all around the West End. They were drawn by children from St Faith's Infant School and St Faith and St Martin Junior School, and they're my favourite pictures EVER. Can you find them? At each picture, scan the QR code, see what I've got to say, and take a fun photo. Find any 6 to finish my trail and win a certificate! Grown-ups, please help little explorers stay safe near roads.",
    "author": "Marc Hanheide",
    "html_title": "The Imp's Night-Time Gallery",
    "project_name": "The Imp's Night-Time Gallery",
    "keywords": "qr, trail, kids, children, lincoln imp, art, gallery, west end lights, lincoln, flask, webapp",
    "upload_folder": "static/uploads/",
    # shown at the top of the trail page before the first find, then under "About this trail"
    "intro": (
        "<p>Psst! Down here! It's me, the <b>Lincoln Imp</b>! 👋</p>"
        "<p>Long, long ago I flew into Lincoln Cathedral and caused SO much mischief that an angel turned me to stone. "
        "I've been sitting high up in the Cathedral ever since... but tonight is West End Lights, so I've sneaked out! Hee hee!</p>"
        "<p>I've turned the West End into my very own <b>Night-Time Gallery</b>. I've hidden <b>11 pictures</b> "
        "all around its streets. They were drawn by children from St Faith's Infant and Nursery School and "
        "St Faith and St Martin Junior School, and they're my favourite pictures EVER!</p>"
        "<p>Can you find <b>6</b> of them? Use my clues to find them, and grown-ups, please help little explorers stay safe near roads.</p>"
    ),
    "required_places": 6,
    # {found}, {required} and {total} are filled in; shown once enough places are found, until all are
    "completion_text": "You did it! You've found {found} of my pictures, so you're an official Imp Gallery Explorer! There are more pictures still hiding if you want to keep looking.",
    "theme": {
        "bg": "#141030",
        "accent": "#ffcf5c",
    },
    "map": {
        "style": "mapbox://styles/mapbox/dark-v11",
        "label_opacity": 0.45,
        "center": [-0.5537, 53.2339],  # [lon, lat]
        "zoom": 16,
        "bounds": [[-0.5610, 53.2300], [-0.5465, 53.2378]],  # [[west, south], [east, north]]
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
            {"max_distance": 20, "text": "Hee hee! You're right next to {title}! Look around for my picture!", "highlight": "success", "vibrate": True},
            {"max_distance": 50, "text": "Ooh, you're getting warmer! {title} is only {distance} away.", "highlight": "warning"},
            {"max_distance": 120, "text": "Keep going, explorer! {title} is close by.", "highlight": "info"},
        ],
    },
    # Stop N shows static/wel-art/art_NN.jpg and stands at point N of trail.geojson.
    # TODO: hints are drafted from OpenStreetMap, check them on site before printing
    "id_dict": {
        "3017ce13-d4e2-48d0-8416-8b0754c95882": {
            "image": "wel-art/art_01.jpg",
            "title": "The Dotty House",
            "text": imp_text(
                "So many dots! Pink dots, blue dots, green dots, orange dots. This house is the dottiest house I've ever seen!",
                "I'm SO famous that Lincoln City football team are called \"the Imps\", after me!",
                "Bounce up and down like a dot of light!",
                "Find the most colourful window you can and take its picture.",
                INFANT_CREDIT,
            ),
            "hint": "Fit for a queen! Find me on curvy <b>Queens Crescent</b>, right by the West Common.",
            "lat": 53.236856,
            "lon": -0.549517,
            "near_text": "🔴🟢🔵 Dotty dotty! The Dotty House is right here!",
        },
        "137d6fba-5478-4b58-af59-2506a1260276": {
            "image": "wel-art/art_02.jpg",
            "title": "The Golden Plesiosaur",
            "text": imp_text(
                "Wow, it's a golden plesiosaur! Say it with me: PLEE-zee-oh-sore! It had a long neck, a tiny head and four big flippers for swimming.",
                "Millions and millions of years ago, the West End was under a warm sea full of plesiosaurs. When St Faith's school was built, the builders dug up a real plesiosaur skeleton, right here in the West End! Even I'm not THAT old!",
                "Stretch your neck up long and tall like a plesiosaur!",
                "Flap your arms like flippers and pretend to swim (on the pavement, not the road!).",
                INFANT_CREDIT,
            ),
            "hint": "Find me where <b>West Parade</b> meets <b>Rosebery Avenue</b>, next to the big, wide West Common.",
            "lat": 53.235827,
            "lon": -0.55575,
            "near_text": "🦕 Splash! The Golden Plesiosaur is right here!",
        },
        "3e26a088-1169-4d82-a45b-55d940948ab0": {
            "image": "wel-art/art_03.jpg",
            "title": "The Big Green Tree",
            "text": imp_text(
                "What a big, bright tree! It has red baubles and a shiny golden star on top. How many baubles can you count?",
                "Light is the fastest thing in the universe. It could zoom all the way round the Earth more than seven times in just one second!",
                "Stand tall like a tree, with your arms as branches.",
                "Find a twinkly tree in a window and take a picture of it.",
                INFANT_CREDIT,
            ),
            "hint": "I'm hiding near a big church called St Faith's, close to <b>Charles Street West</b>.",
            "lat": 53.232943,
            "lon": -0.550731,
            "near_text": "🎄 The Big Green Tree is right here!",
        },
        "6eebd755-0627-40da-8af1-a712705f2b93": {
            "image": "wel-art/art_04.jpg",
            "title": "The Starry Parade",
            "text": imp_text(
                "Stars everywhere! And look at that long line with little windows. Is it a train? A rocket? A street of tiny houses? You decide!",
                "The stars in the night sky are giant suns, just very, very, VERY far away.",
                "Twinkle like a star by opening and closing your hands really fast!",
                "Line up your group like a train and say \"Choo choo!\"",
                INFANT_CREDIT,
            ),
            "hint": "Find me on the corner where <b>Ashlin Grove</b> meets <b>Richmond Road</b>.",
            "lat": 53.233759,
            "lon": -0.5483,
            "near_text": "🌟 The Starry Parade is right here!",
        },
        "01bcc0e5-4a76-4ab5-8ab9-7b7855f625a7": {
            "image": "wel-art/art_05.jpg",
            "title": "The Rainbow Cat",
            "text": imp_text(
                "Miaow! Look at this happy cat with a big round face and a stripy rainbow body! How many colours can you count on its tummy?",
                # TODO: verify the West Common racecourse fact before printing
                "Long ago, there were horse races on the West Common, right here in the West End, for nearly 200 years!",
                "Make cat ears with your fingers and give your happiest cat smile!",
                "Do your best cat stretch and say \"Miaow!\"",
                INFANT_CREDIT,
            ),
            "hint": "I've crept all the way west! Find me on <b>Hewson Road</b>, just up from busy Carholme Road. Hold your grown-up's hand!",
            "lat": 53.234227,
            "lon": -0.559184,
            "near_text": "🐱 Miaow! The Rainbow Cat is right here!",
        },
        "2f1b63af-be84-4ab1-b6dd-6312a3dc2635": {
            "image": "wel-art/art_06.jpg",
            "title": "The Wiggly Fairy Lights",
            "text": imp_text(
                "Red, yellow, green, blue! A long string of fairy lights wiggles right across this picture, with fizzy fireworks all around. Can you spot any letters hiding in there?",
                "The very first West End Lights happened on a snowy night in 2010, with just nine glowing houses. Now more than 40 houses join in!",
                "Hold hands with your group and make a wiggly line like a string of lights.",
                "Count the lights in a twinkly window nearby.",
                JUNIOR_CREDIT,
            ),
            "hint": "Three streets meet here: <b>West Parade</b>, <b>Gresham Street</b> and <b>Hampton Street</b>. Can you find me on the corner?",
            "lat": 53.233926,
            "lon": -0.551017,
            "near_text": "💡 Wiggle wiggle! The Wiggly Fairy Lights are right here!",
        },
        "71e2c65c-296b-452a-b7ce-a33c9c459508": {
            "image": "wel-art/art_07.jpg",
            "title": "The Star Over the Rooftops",
            "text": imp_text(
                "Ooh, look! A giant star is shining down on a row of cosy houses. Can you count how many houses there are?",
                "Lots of houses in the West End are joined together in long rows, like a paper chain. They're called terraced houses!",
                "Make a star shape with your arms and legs!",
                "Find a star in a nearby window and take a picture of it.",
                JUNIOR_CREDIT,
            ),
            "hint": "Neigh! Find me near the horses at the riding school on <b>Newland Street West</b>.",
            "lat": 53.233032,
            "lon": -0.552598,
            "near_text": "⭐ Twinkle twinkle! The Star Over the Rooftops is right here!",
        },
        "ed45a33a-4baa-4652-a2a2-f17f492c5e7e": {
            "image": "wel-art/art_08.jpg",
            "title": "The Midnight Castle",
            "text": imp_text(
                "Wow! A golden building glowing in the middle of the night. It reminds me of my home, the Cathedral! Can you spot the rooftop wearing a Santa hat?",
                "Lincoln Cathedral was once the tallest building in the whole world, even taller than the Great Pyramid!",
                "Point to the tallest thing you can see.",
                "Make a pointy roof with your hands above your head.",
                JUNIOR_CREDIT,
            ),
            "hint": "Sniff sniff, I smell coffee! Find me by the café on <b>Carholme Road</b>, where Depot Street starts. Hold your grown-up's hand!",
            "lat": 53.230932,
            "lon": -0.549077,
            "near_text": "🏰 The Midnight Castle is glowing right here!",
        },
        "282dde8b-cdec-468a-8eb9-419cea9eeff3": {
            "image": "wel-art/art_09.jpg",
            "title": "The Rainbow Swirl Sky",
            "text": imp_text(
                "Swirly whirly! This sky is full of every colour I can think of. Which colour is your favourite?",
                "A rainbow appears when sunlight shines through raindrops. The light splits into red, orange, yellow, green, blue, indigo and violet!",
                "Make your swirliest, twirliest pose (no spinning near the road!).",
                "Find three different coloured lights and take a picture of them.",
                JUNIOR_CREDIT,
            ),
            "hint": "Find me on <b>Hampton Street</b>, near the junior school where some of my artists go!",
            "lat": 53.235271,
            "lon": -0.549168,
            "near_text": "🌈 Swirly whirly! The Rainbow Swirl Sky is right here!",
        },
        "b44c4d83-ea59-480e-921c-af657207e47e": {
            "image": "wel-art/art_10.jpg",
            "title": "The Window Theatre",
            "text": imp_text(
                "Ta-da! The curtains are open and the show is about to begin! What do you think is happening behind that window?",
                "On West End Lights night, lots of front windows turn into tiny theatres and cinema screens, with shadow puppets and pictures glowing out into the street.",
                "Make a shadow puppet with your hands, like a bird or a bunny!",
                "Peek through your fingers like curtains and shout \"Ta-da!\"",
                JUNIOR_CREDIT,
            ),
            "hint": "Find me on <b>West Parade</b>, by the infant school where some of my littlest artists go!",
            "lat": 53.235315,
            "lon": -0.554456,
            "near_text": "🎭 Ta-da! The Window Theatre is right here!",
        },
        "0ffcb0fc-a00d-47ba-9813-58303daa94e4": {
            "image": "wel-art/art_11.jpg",
            "title": "The Cathedral on the Hill",
            "text": imp_text(
                "Look who's up on the hill! It's MY house, Lincoln Cathedral! Down below, families are out for a wintry walk past the twinkly houses. Can you spot the dog? And the sledge with a present on it?",
                "High up in the Cathedral lives a giant bell called Great Tom. It's as heavy as an elephant, and it goes BONG every hour!",
                "Pretend to pull a heavy sledge, or take your pretend dog for a walk!",
                "Look for the Cathedral glowing up on the hill and take a picture of it.",
                JUNIOR_CREDIT,
            ),
            "hint": "Find me where <b>Ely Street</b>, <b>Albert Crescent</b> and <b>Cambridge Avenue</b> meet. Ely has a cathedral, just like my home!",
            "lat": 53.236125,
            "lon": -0.551961,
            "near_text": "⛪ BONG! The Cathedral on the Hill is right here!",
        },
    },
}
