# Open Desk Dash

Open Source Desk Dashboard, a barebone hackable WebUI desk dashboard with Plugin support. Designed to be simple yet easily customisable to fit any need.
Plugins can be easily created, installed and customised. Using Flask and blueprint's to allow an easy way designed Web UI pages that will seemly integrate into the Dashboard and control.

Designed to run on a Raspberry Pi with a screen attached (5", 7"), can support No control, Touch screen, Integrated buttons. Screen size is irrelevant as individual plugins can support any screen size they desire

## Features

- Rotating Dash boards
  - Default Dashboard
  - Default Weather
  - RSS Dash
  - External Site Dash
- Self Updating
- Configurable
- Plugins
  - Easily Modular with Plugins
  - Auto Plugin Update's via github
  - Manual or Automatic install via web interface and github
  - Individual Plugin Database's for customisation
  - framework for plugin Configuration WebUI page

### Backlog

- Theme's
  - Entire Dash theme's overridable
- Pages can have up and down rotation, manually rotated.
- Dashes
  -
  - Spotify dash (show playing, give basic buttons) - use wallpaper as background
- All Dash popups
  - Regardless of what current dash is showing, enable toast pop-ups for emails, messages, etc

### Plugins
Plugins can be developed easily in Python using Flask, see the docs [here](Dev_plugin_guide.md)

```

### Alpha
- Customizable streamdeck, 3x2 grid of custom buttons that call's API's
    - Custom icons, text and API call
- Self auto-update
- find way to restart self
- Easy install Script
