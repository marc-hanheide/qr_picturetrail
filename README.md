# qr_picturetrail
A simple Flask web app for a QR code picture trail. Participants scan QR codes placed around a site, each scan marks a location as found, and groups can upload a photo for every task. Admins can print the QR codes and browse, moderate and delete the uploaded photos.

## Features

- **Trail** (`/trail`): progress tracking per participant session, with a human-readable session ID (e.g. `ambitious-turaco-of-joviality`) and a data consent prompt before taking part.
- **Photo uploads**: PNG, JPG, JPEG and GIF up to 16 MB, automatically rescaled to a maximum of 1024x1024 px. Photos are stored per session in `static/uploads/<session-id>/` together with a `trail.json` record of found items and photos.
- **Reset**: `/?reset=1` clears the current session and starts a new one.
- **Logging**: every QR scan is appended to `log.csv`, which can be downloaded via `/log`.
- **Admin pages** (token protected):
  - `/qrs`: printable QR codes for all trail items.
  - `/gallery`: paginated gallery of all sessions and photos, with options to delete single photos or all sessions.

## Configuration

### Trail content

The trail (title, description, consent text, items with their tasks and hints) is defined in [config.py](config.py) as `app_data`. Each entry in `id_dict` is keyed by a unique ID, which is encoded in its QR code. Alternative trails are kept in separate files (e.g. [config-WEL24.py](config-WEL24.py), [config-WEL26.py](config-WEL26.py)) and selected with the `TRAIL_CONFIG` environment variable. Item images are looked up in `static/` by the `image` name.

### Environment variables (`.env`)

Create a `.env` file in the project root (it is git-ignored). It is loaded automatically by the app and by Docker Compose; variables already set in the shell take precedence.

| Variable | Required | Description |
|---|---|---|
| `TRAIL_ADMIN_ACCESS_TOKEN` | Yes, for admin pages | Secret token granting access to `/qrs`, `/gallery` and the delete endpoints. If unset, all admin pages are denied. |
| `TRAIL_CONFIG` | No | Path (relative to the project root) of the trail config file to load. Defaults to `config.py`. |

Example:

```
TRAIL_ADMIN_ACCESS_TOKEN=change-me-to-a-long-random-secret
TRAIL_CONFIG=config-WEL26.py
```

Use a long random value, e.g. generated with `python -c "import secrets; print(secrets.token_urlsafe(32))"`.

### Admin access

Supply the token once using either:

- a URL parameter: `https://<host>/qrs?token=<TRAIL_ADMIN_ACCESS_TOKEN>`
- an HTTP header: `Authorization: Bearer <TRAIL_ADMIN_ACCESS_TOKEN>`

On success, a signed, HTTP-only cookie valid for 4 weeks is set and you are redirected to the clean URL, so the token does not stay in the address bar. Note that the cookie signing key is regenerated whenever the app restarts, so you need to log in again after a restart.

## Install

1. `python -m venv .venv`
1. `source .venv/bin/activate`
1. `pip install -r requirements.txt`

## Run

### Locally

```
python app.py
```

The app listens on port `5999` (http://localhost:5999).

### Docker Compose

```
docker compose build
docker compose up -d
```

The image is built from [.devcontainer/Dockerfile](.devcontainer/Dockerfile), the project folder is mounted to `/app` (so uploads and `log.csv` persist on the host) and port `5999` is exposed. `TRAIL_ADMIN_ACCESS_TOKEN` and `TRAIL_CONFIG` are taken from `.env`.

### Public deployment

The app respects `X-Forwarded-Proto` and `X-Forwarded-For`, so it can run behind a reverse proxy or tunnel. Generated QR codes use the host the admin page was accessed from, so open `/qrs` via the public URL before printing.

- **zrok**: a commented-out `zrok` service is included in [compose.yml](compose.yml). It additionally requires `ZROK_TOKEN`, `ZROK_API_ENDPOINT`, `ZROK_ENV_NAME` and `ZROK_NAME` in `.env`.
- **ngrok**: `ngrok1 -proto https -subdomain weltrail 5999` (only if you have your own ngrok server available and configured).

## Example trail content (WEL24)



**Page 1: The Sun**

* **Picture:** A bright, cartoon-style sun with a smiley face.
* **Paragraph:** "The sun is a giant ball of burning gas in space. It's so hot that it makes its own light, which travels all the way to Earth to give us sunshine! That's how we can see during the day and feel warm."

**Page 2: Fire**

* **Picture:** A friendly campfire with flames that dance and flicker.
* **Paragraph:** "When things burn, they make light and heat.  A campfire is made of wood burning, and the flames give us light to see in the dark and keep us cosy!"

**Page 3: Light Bulbs**

* **Picture:** A traditional light bulb that glows brightly.
* **Paragraph:** "Inside a light bulb is a tiny wire. When you turn on the light, electricity flows through the wire and makes it get so hot that it glows really bright!"

**Page 5: Fireflies**

* **Picture:** A night scene with fireflies twinkling amongst the grass.
* **Paragraph:** "Fireflies are tiny insects that have their own lights inside their bodies. They use their lights to talk to each other and find friends in the dark!"

**Page 6: The Moon**

* **Picture:** A crescent moon shining in the night sky.
* **Paragraph:** "The moon doesn't make its own light. It's like a giant mirror that reflects the light from the sun. That's why it shines at night!"

**Page 7: Stars**

* **Picture:** A dark night sky filled with twinkling stars.
* **Paragraph:** "Stars are like really, really big suns that are very far away. They make their own light, just like our sun, but they look tiny because they're so far away!" 

Page 8: Lightning

Picture: A fork of lightning illuminating the night sky.

Paragraph: "Lightning is a flash of light that happens in the sky during a thunderstorm. It's really, really bright and can make a loud bang! Lightning is made when electricity builds up in clouds and then jumps to the ground or to another cloud."

Page 9: Light Emitting Diodes (LEDs)

Picture: A circuit board with rows of colorful LEDs illuminated.
Paragraph: "LEDs are tiny lights that are used in lots of things, like TVs, computers, and even Christmas lights! LEDs are very energy-efficient, which means they use less electricity than other types of lights. They also last for a long time, so you don't have to change them as often."