#### Import des modules dash
import dash
import dash_bootstrap_components as dbc

import os
from flask_login import LoginManager, UserMixin
from flask_caching import Cache

from user_mgmt import db, User as base

FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"

#### Initialisation de l'application dash

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY, FONT_AWESOME],
)

#### Paramétrage du cache
cache = Cache(
    app.server, config={"CACHE_TYPE": "filesystem", "CACHE_DIR": "cache-directory"}
)

TIMEOUT = 3600

#### Initialisation du serveur
server = app.server
app.config.suppress_callback_exceptions = True

server.config.update(
    SECRET_KEY=os.urandom(12),
    SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db.init_app(server)

# Setup the LoginManager for the server
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "/"

# Create User class with UserMixin
class User(UserMixin, base):
    pass


# callback to reload the user object
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
