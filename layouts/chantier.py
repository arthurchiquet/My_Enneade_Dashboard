import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import dash_table as dt
import warnings

from server import app
from config import engine
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
                dbc.Label('Paramètres secteur ', size='lg'),
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
        # html.Img(src=app.get_asset_url('test.png')),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(
                                children=[
                                    dbc.Row([modes, options], justify='center'),
                                    dcc.Loading(
                                        color='#FF8C00',
                                        type="graph",
                                        children=dcc.Graph(
                                            id='map-chantier',
                                            config={ "scrollZoom": True},
                                            clear_on_unhover=True,
                                            figure = empty_figure()
                                        )
                                    )
                                ]
                            ), justify='center'
                        ),
                        html.Br(),
                        dcc.Slider(
                            id="preset_slider",
                            disabled=True,
                            min=1,
                            max=3,
                            value=3,
                            dots=True,
                            step=None,
                            marks={
                                1: "30 jrs",
                                2: "60jrs",
                                3: "Tout"
                            },
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
    [Input('mode', 'value'),
    Input("map-chantier", "clickData")])
def display_right_content(mode, clickData):
    if mode==1 and clickData:
        return [
            dbc.Row(dbc.Label(id='titre_graph', size='lg'), justify = 'center'),
            dbc.Row(dbc.Label(id='sous_titre_graph'), justify = 'center'),
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
    Output('preset_slider','disabled'),
    Input('mode', 'value'))
def disabled_slider(mode):
    if mode==3:
        return False
    else:
        return True

@app.callback(
    Output('tabs_content', 'children'),
    [Input('mode', 'value'),
    Input('secteur-store', 'data')]
    )
def return_tabs(mode, secteur):
    if mode == 2 and secteur !={}:
        return [
            dbc.Row(dbc.Button('Afficher / Modifier les parametres', href='/parametres'), justify='center'),
            html.Br(),
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
        return [dbc.Row(html.H4('Veuillez selectionner un secteur sur la carte'), justify='center')]

##### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('affichage_plan','value'),
    Input('mode', 'value'),
    Input('preset_slider', 'value'),
    State('chantier-store', 'data')
    ])
def affichage_map(plan, mode, preset, chantier_store):
    if plan == [1]:
        return affichage_map_chantier(chantier_store, mode, preset, True)
    else:
        return affichage_map_chantier(chantier_store, mode, preset)

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
    Output("courbe_capteur", "figure"),
    Output('sous_titre_graph', 'children')],
    [Input("map-chantier", "clickData"),
    Input('mode', 'value')],
    State('chantier-store', 'data'),
    )
def affichage_courbe_capteur(clickData, mode, chantier):
    if mode != 1:
        return '', empty_figure(), ''
    else:
        try:
            customdata = clickData['points'][0]['customdata'][0]
            text = clickData['points'][0]['text']
            if customdata not in ['cible', 'inclino', 'tirant','jauge','piezo']:
                return '' , empty_figure(), ''
            else:
                return f'{customdata} {text}', selection_affichage(chantier, customdata, text), sous_titre(customdata)
        except:
            return '', empty_figure(), ''


### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, text):
    if customdata == 'cible':
        return utils_topo.graph_topo(chantier, text, 0, height = 450, spacing=0.06)
    elif customdata == 'inclino':
        return utils_inclino.graph_inclino(chantier, text)
    elif customdata == 'tirant':
        return utils_tirant.graph_tirant(chantier, text, mode=2)
    elif customdata == 'jauge':
        return utils_jauge.graph_jauge(chantier, text)
    elif customdata == 'piezo':
        return utils_piezo.graph_piezo(chantier, text)
    else:
        return empty_figure()

def sous_titre(customdata):
    if customdata == 'cible':
        return 'Déplacements N, T, Z (mm)'
    elif customdata == 'inclino':
        return ''
    elif customdata == 'tirant':
        return 'Evolution de la charge (%tb)'
    elif customdata == 'jauge':
        return 'Evolution brute des fissures (Ecarts, mm)'
    elif customdata == 'piezo':
        return 'Niveau piezométrique (mm)'
    else:
        return ''


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

