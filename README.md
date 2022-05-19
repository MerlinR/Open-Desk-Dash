# Open-Desk-Dash
Open Source Desk Dashboard, an Pi desk dashboard that can interface to a running computer to displays system information and other information the user may wish.
The Dash has two components:

## Pi display
The Pi display service, this can run independently to act as a dashboard.

## Desktop Service
A service that runs on the your desktop that acts as an interface to the PI, so it can query the desktop for information.

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