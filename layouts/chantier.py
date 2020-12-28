import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import dash_table as dt
import warnings
import json

from server import app
from config import engine
from data import get_data
from utils_maps import affichage_map_chantier, empty_figure
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}

tabs_content = html.Div(id='tabs_content')

dropdowns = dcc.Dropdown(
                id='mode',
                persistence=True,
                persistence_type="session",
                options=[
                {'label': 'Positions GPS', 'value': 'GPS'},
                {'label': 'Secteurs', 'value': 'secteurs'},
                {'label': 'Vecteurs', 'value': 'vecteurs'},
                ],
                value='GPS',
                style={'color':'black'}
            )

options = dbc.Checklist(
    options=[
        {"label": "Afficher / masquer le plan", "value": 1},
    ],
    value=[],
    id="affichage_plan",
    inline=True,
    switch=True
)

layout = html.Div(
    children=[
        html.Br(),
        dbc.Row(
            children=[
                dbc.Button('Vue générale', color = 'dark', className="mr-1", href='/'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')
            ], justify='center'
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dropdowns,
                        options,
                        dbc.Row(
                            dbc.Container(
                                children=[
                                dcc.Graph(
                                    id='map-chantier',
                                    config={ "scrollZoom": True},
                                    clear_on_unhover=True)
                                ], fluid=True
                            )
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(dbc.Label(id='titre_graph', size='lg'), justify = 'center'),
                        html.Br(),
                        dbc.Container(
                            children=[
                            dcc.Loading(
                                id = "loading-graph",
                                color='#FF8C00',
                                type="graph",
                                children = dcc.Graph(id='courbe_capteur', config={"scrollZoom": True})
                                )
                            ], fluid=True
                        )
                    ]
                )
            ]
        ),
        html.Br(),
        html.Hr(),
        tabs_content,
    ]
)


@app.callback(
    Output('tabs_content', 'children'),
    Input('mode', 'value'))
def return_tabs(mode):
    if mode == 'secteurs':
        return [
            dbc.Row(
                dbc.Tabs(
                    [
                        dbc.Tab(label="Cibles", tab_id=1),
                        dbc.Tab(label="Inclinomètres", tab_id=2),
                        dbc.Tab(label="Tirants", tab_id=3),
                        dbc.Tab(label="Piezometres", tab_id=5),
                        dbc.Tab(label="Jauges", tab_id=4),
                        dbc.Tab(label="Butons", tab_id=6),
                    ],
                    id="tabs_secteurs",
                    active_tab="tab-topo",
                ), justify='center'
            ),
            html.Br(),
            html.Div(id='tab_content')
        ]
    else:
        return []

##### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('affichage_plan','value'),
    Input('mode', 'value'),
    State('chantier-store', 'data')
    ])
def affichage_map(plan, mode, chantier_store):
    if plan == [1]:
        return affichage_map_chantier(chantier_store, mode, True)
    else:
        return affichage_map_chantier(chantier_store, mode)


@app.callback(
    Output('hover-data', 'children'),
    Input('map-chantier', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)

##### STOCKE LA VALEUR DU SECTEUR ####
@app.callback(
    Output('secteur-store', 'data'),
    [Input('map-chantier', 'clickData'),
    Input('mode', 'value')])
def click(clickData, mode):
    if mode =='secteurs' and clickData:
        return clickData['points'][0]['hovertext']
    else:
        return {}

#### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [Output('titre_graph', 'children'),
    Output("courbe_capteur", "figure")],
    [Input("map-chantier", "clickData"),
    Input('mode', 'value')],
    State('chantier-store', 'data'),
    )
def affichage_courbe_capteur(clickData, mode, chantier):
    if mode != 'GPS':
        return '', empty_figure()
    else:
        try :
            customdata = clickData['points'][0]['customdata'][0]
            hovertext = clickData['points'][0]['hovertext']
            return f'{customdata} : {hovertext}', selection_affichage(chantier, customdata, hovertext)
        except:
            return '', empty_figure()


#### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, hovertext):
    if customdata == 'cible':
        return utils_topo.graph_topo(chantier, hovertext, 0, height = 550)
    elif customdata == 'inclino':
        return utils_inclino.graph_inclino(chantier, hovertext)
    elif customdata == 'tirant':
        return utils_tirant.graph_tirant(chantier, hovertext)
    elif customdata == 'jauge':
        return utils_jauge.graph_jauge(chantier, hovertext)
    elif customdata == 'piezo':
        return utils_piezo.graph_piezo(chantier, hovertext)


@app.callback(
    Output('tab_content', 'children'),
    [Input('tabs_secteurs', 'active_tab'),
     Input('chantier-store', 'data'),
     Input('secteur-store', 'data')
    ])
def return_tabs_content(tab, chantier, secteur):
    if secteur=={}:
        return dbc.Row(html.H4('Veuillez selectionner un secteur sur la carte'), justify='center')
    else:
        if tab == 1:
            return utils_topo.layout
        elif tab == 2:
            return utils_inclino.layout
        elif tab == 3:
            return utils_tirant.layout
        elif tab == 4:
            return utils_jauge.layout
        elif tab == 5:
            return utils_piezo.layout


# @app.callback(
#     [Output("table_param", "data"),
#     Output("table_param", "columns")],
#     Input("map-chantier", "hoverData"),
#     State('mode', 'value')
# )
# def update_table_param(hoverData, mode):
#     try:
#         customdata = hoverData['points'][0]['customdata'][0]
#         hovertext = hoverData['points'][0]['hovertext']
#         if mode == 'GPS':
#             with engine.connect() as con:
#                 query=f"select * from {customdata}_param where {customdata}='{hovertext}'"
#                 parametres = pd.read_sql_query(query, con=con)
#             return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]
#         if mode == 'secteurs':
#             with engine.connect() as con:
#                 query=f"select * from secteur where secteur='{hovertext}'"
#                 parametres = pd.read_sql_query(query, con=con)
#             return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]
#         else:
#             return [],[]
#     except:
#         return [],[]
