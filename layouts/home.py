import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import dash_table as dt
from flask_login import current_user
from utils_maps import affichage_map_geo
from data import get_data, download_json
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
        html.Div(id = 'progress-bar'),
        dcc.Graph(
            id='map-geo',
            config={'displayModeBar': False},
            figure=affichage_map_geo(),
        )
    ]
)

@app.callback(
    Output("progress-bar", "children"),
    Input('map-geo', 'clickData')
)
def display_progress(clickdata):
    if clickdata:
        return dcc.Interval(id="progress-interval", n_intervals=0, interval=1000),dbc.Progress(id="progress", color="warning")
    else:
        return []

@app.callback(
    [Output("progress", "value"),
    Output("progress", "children")],
    [Input('map-geo', 'clickData'),
     Input("progress-interval", "n_intervals")],
)
def update_progress(clickdata, n):
    if clickdata:
        progress = min(15*n , 100)
        return progress, f"{progress} %" if progress >= 5 else ""
    else:
        return 0, ''

##### SELECTIONNE CHANTIER #####
@app.callback(
    [Output('chantier-store', 'data'),
    Output('url', 'pathname'),
    Output('files-store', 'data')],
    Input('map-geo', 'clickData'),
    State('files-store', 'data'))
def store_chantier(clickData, data):
    try:
        chantier = clickData['points'][0]['hovertext']
        data['topo'] = get_data(chantier, 'actif', 'topographie.json', json=True, sep=False).to_json()
        return chantier, '/chantier', data
    except:
        return None, '/', data

