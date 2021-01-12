import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import dash_table as dt
from flask_login import current_user
from utils_maps import affichage_map_geo
from data import get_data
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
        html.Div(id='progress-bar'),
        dcc.Graph(
            id='map-geo',
            config={'displayModeBar': False},
            figure=affichage_map_geo(),
        )
    ]
)

##### SELECTIONNE CHANTIER #####
@app.callback(
    [Output('chantier-store', 'data'),
    Output('url', 'pathname'),
    Output('files-store', 'data')],
    Input('map-geo', 'clickData'),
    State('files-store', 'data'))
def select_chantier(clickData, data):
    try:
        chantier = clickData['points'][0]['hovertext']
        data['topo'] = get_data(chantier, 'actif', 'topographie.json', json=True, sep=False).to_json()
        return chantier, '/chantier', data
    except:
        return None, '/', data


@app.callback(
    Output("progress-bar", "children"),
    Input('map-geo', 'clickData'),
)
def update_progress(clickData):
    if clickData:
        return [dcc.Interval(id="progress-interval", n_intervals=0, interval=1000),dbc.Progress(id="progress", color="warning")]
    else:
        return []

@app.callback(
    [Output("progress", "value"), Output("progress", "children")],
    [Input("progress-interval", "n_intervals")],
)
def update_progress(n):
    # check progress of some background process, in this example we'll just
    # use n_intervals constrained to be in 0-100
    progress = min(20*n , 100)
    # only add text after 5% progress to ensure text isn't squashed too much
    return progress, f"{progress} %" if progress >= 5 else ""
