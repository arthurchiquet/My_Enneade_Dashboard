#### import des modules dash

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table as dt

#### Import des librairies

import pandas as pd
import warnings

from server import app
from config import engine
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

warnings.filterwarnings("ignore")

layout = html.Div(
    [
        html.Br(),
        dbc.Row(html.H4(id="secteur-title"), justify="center"),
        html.Hr(style=dict(width="400px")),
        dbc.Row(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(
                            labelClassName="far fa-dot-circle", tab_id=1, id="topo"
                        ),
                        dbc.Tab(labelClassName="fas fa-slash", tab_id=2, id="inclino"),
                        dbc.Tab(
                            labelClassName="fas fa-arrows-alt-h", tab_id=3, id="tirant"
                        ),
                        dbc.Tab(
                            labelClassName="fab fa-cloudscale", tab_id=4, id="jauge"
                        ),
                        dbc.Tab(labelClassName="fas fa-water", tab_id=5, id="pizeo"),
                        # dbc.Tab(labelClassName="far fa-dot-circle", tab_id=6),
                    ],
                    id="tabs_type",
                    active_tab=1,
                    persistence=True,
                    persistence_type="session",
                ),
            ],
            justify="center",
        ),
        html.Br(),
        html.Div(id="tab_type_content"),
    ]
)


#### Affiche en titre le nom du secteur sélectionné
@app.callback(
    Output("secteur-title", "children"),
    Input("secteur-select", "data"),
)
def return_title(secteur_selected):
    if secteur_selected == {}:
        return "Aucun secteur sélectionné"
    else:
        return f'Secteur {secteur_selected["secteur"]}'

#### En fonction de l'onglet sélectionné renvoie l'interface (page) correspond
#### au type de mesures à afficher
@app.callback(
    Output("tab_type_content", "children"),
    [Input("tabs_type", "active_tab")],
    [State("chantier-select", "data"), State("secteur-select", "data")],
)
def return_tabs_content(tab, chantier, secteur):
    if tab == 1:

        ''' onglet 1 : Mesures topographiques'''

        return utils_topo.layout

    elif tab == 2:

        ''' onglet 2 : Mesures inclinométriques'''

        return utils_inclino.layout

    elif tab == 3:

        ''' onglet 3 : Mesures tirants'''

        return utils_tirant.layout

    elif tab == 4:

        ''' onglet 4 : Mesures jauges'''

        return utils_jauge.layout

    elif tab == 5:

        ''' onglet 5 : Mesures piezométriques'''

        return utils_piezo.layout
