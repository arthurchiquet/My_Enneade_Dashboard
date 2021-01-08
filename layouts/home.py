import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import dash_table as dt
from flask_login import current_user
from utils_maps import affichage_map_geo
from config import engine
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}

layout = html.Div(
    [
        dcc.Loading(
            id = "loading-map-geo",
            color='#FF8C00',
            type="cube",
            children = dcc.Graph(
                id='map-geo',
                config={'displayModeBar': False},
                figure=affichage_map_geo(),
            )
        )
    ]
)


##### SELECTIONNE CHANTIER #####
@app.callback(
    [Output('chantier-store', 'data'),
    Output('url', 'pathname')],
    Input('map-geo', 'clickData'))
def select_chantier(clickData):
    try:
        chantier = clickData['points'][0]['hovertext']
        return chantier, '/chantier'
    except:
        return None, '/'
