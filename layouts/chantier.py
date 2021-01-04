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

modes = dbc.RadioItems(
    options=[
        {"label": "Capteurs", "value": 1},
        {"label": "Secteurs", "value": 2},
        {"label": "Vecteurs", "value": 3},
    ],
    value=1,
    id="mode",
    inline=True,
    persistence=True,
    persistence_type="local"
)

options = dbc.Checklist(
    options=[
        {"label": "Afficher / masquer le plan", "value": 1},
    ],
    value=[],
    id="affichage_plan",
    inline=True,
    switch=True,
    persistence=True,
    persistence_type="local"
)


layout = html.Div(
    children=[
        html.Br(),
        dbc.Row(
            children=[
                dbc.Button('Vue générale', color = 'dark', className="mr-1", href='/'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Export PDF', color = 'light', className="mr-1"),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')
            ], justify='center'
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(
                                children=[
                                dbc.Row([modes, options], justify='center'),
                                dcc.Graph(
                                    id='map-chantier',
                                    config={ "scrollZoom": True},
                                    clear_on_unhover=True,
                                    figure = empty_figure()
                                )
                                ]
                            ), justify='center'
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(
                                id='right-content',
                                children=[]
                            ), justify='center'
                        )
                    ]
                )
            ]
        ),
        html.Br(),
        html.Hr(),
        dbc.Row(html.H4(id='title_secteur'), justify='center'),
        tabs_content,
    ]
)


@app.callback(
    Output('right-content', 'children'),
    Input('mode', 'value'))
def display_right_content(mode):
    if mode==1:
        return [
            dbc.Row(dbc.Label(id='titre_graph', size='lg'), justify = 'center'),
            dcc.Loading(
                id = "loading-graph",
                color='#FF8C00',
                type="graph",
                children = dcc.Graph(id='courbe_capteur')
            )
        ]
    elif mode==2:
        return []
    elif mode==3:
        return []



@app.callback(
    Output('tabs_content', 'children'),
    [Input('mode', 'value'),
    Input('secteur-store', 'data')]
    )
def return_tabs(mode, secteur):
    if mode == 2 and secteur !={}:
        return [
            html.Hr(style=dict(width=500)),
            dbc.Row(
                [
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
                    )
                ], justify='center'
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

##### STOCKE LA VALEUR DU SECTEUR ####
@app.callback(
    Output('secteur-store', 'data'),
    Input('map-chantier', 'clickData'),
    State('mode', 'value'))
def secteur_store(clickData, mode):
    if mode ==2 and clickData:
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
    if mode != 1:
        return '', empty_figure()
    else:
        try :
            customdata = clickData['points'][0]['customdata'][0]
            text = clickData['points'][0]['text']
            return f'{customdata} : {text}', selection_affichage(chantier, customdata, text)
        except:
            return '', empty_figure()


#### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, text):
    if customdata == 'cible':
        return utils_topo.graph_topo(chantier, text, 0, height = 450)
    elif customdata == 'inclino':
        return utils_inclino.graph_inclino(chantier, text)
    elif customdata == 'tirant':
        return utils_tirant.graph_tirant(chantier, text)
    elif customdata == 'jauge':
        return utils_jauge.graph_jauge(chantier, text)
    elif customdata == 'piezo':
        return utils_piezo.graph_piezo(chantier, text)


@app.callback(
    Output('tab_content', 'children'),
    [Input('tabs_secteurs', 'active_tab'),
     Input('chantier-store', 'data'),
     Input('secteur-store', 'data')
    ])
def return_tabs_content(tab, chantier, secteur):
    if secteur=={}:
        return {}
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


@app.callback(
    Output('title_secteur', 'children'),
    [Input('mode', 'value'),
     Input('secteur-store', 'data')
    ])
def title_secteur(mode, secteur):
    if mode == 2 and secteur !={}:
        return f'Bilan secteur : {secteur}'
    elif mode == 2:
        return 'Veuillez selectionner un secteur sur la carte'
    else:
        return ''



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
