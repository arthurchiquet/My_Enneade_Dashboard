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
from utils_topo import graph_topo, format_df
from utils_inclino import graph_inclino
# from utils_tirant import graph_tirant
# from utils_piezo import graph_piezo
from utils_jauge import graph_jauge

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}

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
                style={"width": "50%", 'color':'black'}
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
                        dbc.Row(dropdowns, justify = 'center'),
                        dbc.Row(
                            dbc.Container(
                                children=[
                                dcc.Loading(
                                    id = "loading-map-chantier",
                                    color='#FF8C00',
                                    type="dot",
                                    children = dcc.Graph(id='map-chantier', config={'displayModeBar': False, "scrollZoom": True})
                                    )
                                ], fluid=True
                            )
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(dbc.Label(id='tire_graph', size='lg'), justify = 'center'),
                        html.Br(),
                        # dbc.Row(
                        #     dbc.Container(
                        #         dt.DataTable(
                        #             id="table_param",
                        #             editable=True,
                        #             style_cell={
                        #                 'backgroundColor': 'rgb(50, 50, 50)',
                        #                 'color': 'white',
                        #                 'minWidth': '180px',
                        #                 'width': '180px',
                        #                 'maxWidth': '180px',
                        #                 'textAlign': 'center'
                        #                 },
                        #             ),
                        #     )
                        # ),
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
        dbc.Row(dbc.Col(id='buttons-secteurs', children=[], width={"size": 5, "offset": 1}))
    ]
)


##### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('chantier-store', 'data'),
    Input('mode', 'value')])
def affichage_map(chantier_store, mode):
    return affichage_map_chantier(chantier_store, mode)


##### AFFICHE LES BOUTONS DE RAPPORTS LORSQU'UN SECTEUR EST SELECTIONNE  ET STOCKE LA VALEUR DU SECTEUR ####
@app.callback(
    [Output('buttons-secteurs', 'children'),
    Output('secteur-store', 'data')],
    Input('map-chantier', 'clickData'),
    Input('mode', 'value'))
def click(clickData, mode):
    if mode =='secteurs' and clickData:
        content = [
            dbc.Button('Topo', href='/secteur', className="mr-1", id='topo', n_clicks=0),
            dbc.Button('Inclino', href='/secteur', className="mr-1", id="inclino", n_clicks=0),
            dbc.Button('Tirant', href='/secteur', className="mr-1", id='tirant', n_clicks=0),
            dbc.Button('Jauge', href='/secteur', className="mr-1", id='jauge', n_clicks=0),
            dbc.Button('Piezo', href='/secteur', className="mr-1", id='piezo', n_clicks=0)
        ]
        return content, clickData['points'][0]['hovertext']
    else:
        return [], {}


##### RENVOI VERS LE RAPPORT CORRESPONDANT #####
@app.callback(
    Output('type-store', 'data'),
    [Input('topo', 'n_clicks'),
    Input('inclino', 'n_clicks'),
    Input('tirant', 'n_clicks'),
    Input('jauge', 'n_clicks'),
    Input('piezo', 'n_clicks')])
def click(n_clicks_1, n_clicks_2, n_clicks_3, n_clicks_4, n_clicks_5):
    if n_clicks_1 > 0:
        return 1
    elif n_clicks_2 > 0:
        return 2
    elif n_clicks_3 > 0:
        return 3
    elif n_clicks_4 > 0:
        return 4
    elif n_clicks_5 > 0:
        return 5


#### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [Output('tire_graph', 'children'),
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
        return graph_topo(chantier, hovertext, 0)
    elif customdata == 'inclino':
        return graph_inclino(chantier, hovertext)
    elif customdata == 'tirant':
        return graph_tirant(chantier, hovertext)
    elif customdata == 'jauge':
        return graph_jauge(chantier, hovertext)
    elif customdata == 'piezo':
        return graph_piezo(chantier, hovertext)

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
