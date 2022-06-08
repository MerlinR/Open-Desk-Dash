# Open Desk Dash

Open Source Desk Dashboard, a barebone hackable WebUI desk dashboard with Plugin support. Designed to be simple yet easily customisable to fit any need.
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

### Backlog
- Theme's
    - Entire Dash theme's overridable
- Pages can have up and down rotate, for slight variants of same page
- All Dash popups
    - Regardless of what current dash is showing, enable toast popups for emails, messages, etc

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

- Dashes
    - Default dash RSI feed - news / hackaday
    - Customizable streamdeck, 3x2 grid of custom buttons that call's API's
        - Custom icons, text and API call
    - Spotify dash (show playing, give basic buttons) - use wallpaper as background
    - Dash that displays external sites and use iframe in base template for rotation
- Self auto-update
- find way to restart self
- Easy install Script