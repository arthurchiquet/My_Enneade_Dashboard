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

profil=1

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

secteur_params = [
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                dbc.Label('Paramètres secteur : ', size='lg'),
                width={"size": 3.5, "offset": 3},
            ),
            dbc.Col(
                dbc.Label(id='titre_secteur', size='lg'),
                width={"size": 2, "offset": 0},
            )
        ]
    ),
    html.Br(),
    dbc.Row(
        [
            dbc.Col(
                [
                    dbc.Label("Parametre 1:   "),
                    html.Br(),
                    html.Br(),
                    dbc.Label("Parametre 2:   "),
                    html.Br(),
                    html.Br(),
                    dbc.Label("Parametre 3:   "),
                    html.Br(),
                    html.Br(),
                    dbc.Label("Parametre 4:   "),
                    html.Br(),
                    html.Br(),
                    dbc.Label("Parametre 5:   "),
                    html.Br(),
                    html.Br(),
                    dbc.Label("Parametre 6:   "),
                ],
                width={"size": 3.5, "offset": 3}
            ),
            dbc.Col(
                [
                    dbc.Label(id="Parametre 1", className="text-success"),
                    html.Br(),
                    html.Br(),
                    dbc.Label(id="Parametre 2", className="text-success"),
                    html.Br(),
                    html.Br(),
                    dbc.Label(id="Parametre 3", className="text-success"),
                    html.Br(),
                    html.Br(),
                    dbc.Label(id="Parametre 4", className="text-success"),
                    html.Br(),
                    html.Br(),
                    dbc.Label(id="Parametre 5", className="text-success"),
                    html.Br(),
                    html.Br(),
                    dbc.Label(id="Parametre 6", className="text-success"),

                ],
            ),
        ]
    )
]

layout = html.Div(
    children=[
        html.Br(),
        dbc.Row(
            id='options-buttons',
            children=[],
            justify='center'
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
    Output('options-buttons','children'),
    Input('page-content', 'children'))
def options_buttons(content):
    if profil==1:
        return [
                dbc.Button('Vue générale', color = 'dark', className="mr-1", href='/'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Admin', id= 'profil', color='dark', className="mr-1", href='admin'),
                dbc.Button('Export PDF', color = 'light', className="mr-1"),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')]
    else :
        return [
                dbc.Button('Vue générale', color = 'dark', className="mr-1", href='/'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Export PDF', color = 'light', className="mr-1"),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')]


@app.callback(
    Output('right-content', 'children'),
    [Input('mode', 'value'),
    Input("map-chantier", "clickData")])
def display_right_content(mode, clickData):
    if mode==1 and clickData:
        return [
            dbc.Row(dbc.Label(id='titre_graph', size='lg'), justify = 'center'),
            dcc.Loading(
                id = "loading-graph",
                color='#FF8C00',
                type="graph",
                children = dcc.Graph(id='courbe_capteur', figure = empty_figure())
            )
        ]
    elif mode==2:
        return secteur_params
    elif mode==3:
        return []
    else:
        return []


@app.callback(
    Output('titre_secteur', 'children'),
    Output('Parametre 1', 'children'),
    Output('Parametre 2', 'children'),
    Output('Parametre 3', 'children'),
    Output('Parametre 4', 'children'),
    Output('Parametre 5', 'children'),
    Output('Parametre 6', 'children'),
    [Input('mode', 'value'),
    Input('secteur-store', 'data')]
    )
def return_secteurs_params(mode, secteur):
    if mode == 2 and secteur !={}:
        with engine.connect() as con:
            query=f"select * from secteur where secteur='{secteur}'"
            parametres = pd.read_sql_query(query, con=con)
        param_1= parametres.angle[0]
        param_2= parametres.seuil_alerte[0]
        param_3= parametres.seuil_intervention[0]
        param_4= parametres.affichage[0]
        param_5=""
        param_6=""
        return secteur, param_1, param_2, param_3, param_4, param_5, param_6
    else:
        return "", "", "", "", "", "", ""

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
        return clickData['points'][0]['text']
    else:
        return {}

### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
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
        try:
            customdata = clickData['points'][0]['customdata'][0]
            text = clickData['points'][0]['text']
            if customdata not in ['cible', 'inclino', 'tirant','jauge','piezo']:
                return '', empty_figure()
            else:
                return f'{customdata} : {text}', selection_affichage(chantier, customdata, text)
        except:
            return '', empty_figure()



### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, text):
    if customdata == 'cible':
        return utils_topo.graph_topo(chantier, text, 0, height = 450, spacing=0.06)
    elif customdata == 'inclino':
        return utils_inclino.graph_inclino(chantier, text)
    elif customdata == 'tirant':
        return utils_tirant.graph_tirant(chantier, text)
    elif customdata == 'jauge':
        return utils_jauge.graph_jauge(chantier, text)
    elif customdata == 'piezo':
        return utils_piezo.graph_piezo(chantier, text)
    else:
        return empty_figure()


@app.callback(
    Output('tab_content', 'children'),
    [Input('mode', 'value'),
    Input('tabs_secteurs', 'active_tab')],
    [State('chantier-store', 'data'),
    State('secteur-store', 'data')])
def return_tabs_content(mode, tab, chantier, secteur):
    if secteur=={} or mode !=2:
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

