# Developing Open Desk Dash plugins

Open Desk Dash can easily be extended with Plugins, by creating a flask blueprint and inserting/uploading the module into the "plugins" directory.
The blueprint module directory name and primary python script must have the same name, and the blueprint must be called api.

## Important Notes

### Plugin Name override

The plugin name is likely going to be altered during installation, this is to avoid duplicates. This happens when installing a Plugin via the github link. It will pre-append author name to the front, this will carry on throughout, although the registry title will remain the same. E:G MerlinR/ODDash_stock_watcher -> MerlinR_stock_watcher

# Layout
```
└── plugin_name
    ├── registry.toml
    ├── requirements.txt
    ├── src
    │   ├── static
    │   │   ├── css
    │   │   │   └── styles.css
    │   │   └── js
    │   └── plugin_name
    │       └── watcher.html
    └── plugin_name.py
```

# Registry file
```
[plugin]
title = "My Fancy Plugin Name"
description = "My fucking amazing plugin description<br>supports html!"
author = "MerlinR"
github = "https://github.com/MerlinR/plugin_name"
version = "1.0"
```

# Main Blueprint Script
```
api = Blueprint("plugin_name", __name__)
```

# Dash page


# Config's

You can create as many plugin's as you want for your app, these will be automatically saved into ODDash config DB, where it's persistent across reboots.

## Creating Config's

Config's can be easily created within a setup function, this function is optional and expected to reside within the plugin.py file. Setup function expects the flask App as an argument to then run commands in the context.

Using the API [create_config](#create_config) function to generate the DB config table and default fields. This will not overwrite any existing config values.

Below is an example of creating a config for the apideck_dash plugin along with default values.

```
def setup(app: Flask):
    with app.app_context():
        current_app.create_config(
            {
                "title": str,
                "iconSize": int,
                "iconRadius": int,
            },
            {
                "title": "API Deck",
                "iconSize": "84",  # In pixels
                "iconRadius": "20",  # In percent 0 = square 50 = circle
            },
        )
```

## Using Config's
### Within Template
### Within python Blueprint

## Adding Config page

# Blueprint API

To help the plugins function and work independently more easily the Flask App has been extended, several functions have been made and added. These are designed to make developing plugins more easily, these can all be used with the `current_app`.

##### Table of Contents

- [Database](#Database)
  - [create_config](#create_config)
  - [gather_config](#gather_config)
  - [save_config](#save_config)
  - [create_db](#create_db)
  - [connect_db](#connect_db)
- [Utils](#Utils)  
  - [plugin_path](#plugin_path)

## Database

### create_config

`create_config(schema: dict, init_data: dict = None) -> None`
create_config is a custom API function added to the Flask App to allow plugins to create there own persistent configurations. This is essentially an abstraction to a sqlite database stored within the app.
Therefore the data types must link to sqlite data types:

data types:

- str
- int
- float
- list
- None (blob)

As list's are not accept in sqlite the script will convert a list into a comma separated string to be saved, when reading it back out of the it will still be a list, therefore it's up to you to conver it back into a list, this can be done with a split, `config.split(',')`.

#### Example

```
def setup(app: Flask):
    with app.app_context():
        current_app.create_config(
            {
                "title": str,
                "iconSize": int,
            },
            {
                "title": "API Deck",
                "iconSize": "24",  # In pixels
            },
        )
```

### gather_config

### save_config
#### Example
```
current_app.save_config(
    {
        "title": request.form["dash_title"],
        "iconSize": request.form["icon_size"],
    }
)
```

### create_db
#### Example
```
def setup(app: Flask):
    with app.app_context():
        current_app.create_db(
            """
            CREATE TABLE buttons (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
            );
        """
        )
```

### connect_db

returns sqlite3.Connection

## Utils

### plugin_path

`plugin_path() -> str` has been added to easily get the path from the App to your local plugin Dir, the purpose is to avoid hardcoded naming. This is important as Plugins may have there own names changed during installation.

#### Example

```
> current_app.plugin_path()
plugins/<NAME>/

```

# Jinga2(template) API

## plugin_config
Used to get your plugin Config's
```
{{plugin_config('iconRadius')}}
```


# Helpful tips
## Importing href resources
When calling local files using "url_for" ensure you dont specify the blueprint name, this is due to the likely hood ODDash will rename the blueprint/route. Therefore to ensure the URL path is correct use a relative path E.G:

```
<link rel="stylesheet" href={{ url_for('.static', filename='css/styles.css') }}>
``` 

## Calling back

As stated the plugin/blueprint name may change, to avoid this issues there should be not hardcoded instances of te blueprint name within the plugin, an easy solution within Jinga2 templates is to get the blueprint name via requests:

```
{{request.blueprint}}
```

This will return the current blueprint name.