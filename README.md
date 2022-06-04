# Open Desk Dash

Open Source Desk Dashboard, a barebone hackable WebUI desk dashboard with Plugin support. Designed to be simple, elegant and easily customisable to fit any need.
Plugins can be easily created, installed and customised. Using Flask and blueprint's to allow an easy way designed Web UI pages that will seemly integrate into the Dashboard and control.

Designed to run on a Raspberry Pi with a screen attached (5", 7"), can support No control, Touch screen, Integrated buttons. Screen size is irrelevant as individual plugins can support any screen size they desire

## Features

- Configuration
    - Usage configurable
- Plugins
    - Easily Modular with Plugins
    - Auto Plugin Update's via github
    - Manual or Automatic install via web interface and github
    - Individual Plugin Database's for customisation
    - framework for plugin Configuration WebUI page

### To Do
- Theme's
    - Entire Dash theme overridable
- Pages can have up and down rotate, for slight variants of same page
- Allow external sites and use iframe in base template for rotation

### Plugins

The desktop service API can easily be extended with Plugins, by creating a flask blueprint and inserting the module into the "plugins" directory.
The blueprint module directory name and primary python script must have the same name, and the blueprint must be called api.

```
├── plugins
│   ├── example
│   │   ├── example.py
│   │   ├── __init__.py
```

```
api = Blueprint("example", __name__, url_prefix="/example")
```

## To-Do

### Alpha

- Self auto-update
- Easy install Script
