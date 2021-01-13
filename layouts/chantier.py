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

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

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
        # html.Img(src=app.get_asset_url('test.png'))
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
                                        figure = empty_figure()
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
        html.Div([
            dcc.Markdown("""
                **Hover Data**
            """),
            html.Pre(id='hover-data', style=styles['pre'])
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Click Data**
            """),
            html.Pre(id='click-data', style=styles['pre']),
        ], className='three columns'),

        html.Div([
            dcc.Markdown("""
                **Selection Data**
            """),
            html.Pre(id='selected-data', style=styles['pre']),
        ], className='three columns'),
    ]
)

##### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('affichage_plan','value'),
    Input('mode', 'value'),
    Input('preset_slider', 'value'),
    State('chantier-store', 'data'),
    State('files-store', 'data'),
    ])
def affichage_map(plan, mode, preset, chantier_store, data):
    return affichage_map_chantier(data, chantier_store, mode, preset, plan)

@app.callback(
    Output('hover-data', 'children'),
    Input('map-chantier', 'hoverData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)


@app.callback(
    Output('click-data', 'children'),
    Input('map-chantier', 'clickData'))
def display_click_data(clickData):
    return json.dumps(clickData, indent=2)


@app.callback(
    Output('selected-data', 'children'),
    Input('map-chantier', 'selectedData'))
def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


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


conv = {0:'Cible',1:'Inclinometre',2:'Tirant',3:'Jauge',4:'Piezometre',5:'Buton'}

### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [Output('titre_graph', 'children'),
    Output("courbe_capteur", "figure"),
    Output('sous_titre_graph', 'children')],
    [Input("map-chantier", "clickData"),
    Input('mode', 'value')],
    State('chantier-store', 'data'),
    State('files-store', 'data')
    )
def affichage_courbe_capteur(clickData, mode, chantier, data):
    if mode != 1:
        return '', empty_figure(), ''
    else:
        try:
            curveNumber = clickData['points'][0]['curveNumber']
            text = clickData['points'][0]['text']
            if curveNumber > 6 :
                return '' , empty_figure(), ''
            else:
                return f'{conv[curveNumber]} {text}', selection_affichage(data, chantier, curveNumber, text), sous_titre(curveNumber)
        except:
            return '', empty_figure(), ''


### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(data, chantier, curveNumber, text):
    if curveNumber == 0:
        return utils_topo.graph_topo(data['topo'], chantier, text, 0, height = 450, spacing=0.06)
    elif curveNumber == 1:
        return utils_inclino.graph_inclino(chantier, text)
    elif curveNumber == 2:
        return utils_tirant.graph_tirant(chantier, text, height = 450, mode=2)
    elif curveNumber == 3:
        return utils_jauge.graph_jauge(chantier, text)
    elif curveNumber == 4:
        return utils_piezo.graph_piezo(chantier, text)
    else:
        return empty_figure()

def sous_titre(curveNumber):
    if curveNumber == 1:
        return 'Déplacements N, T, Z (mm)'
    elif curveNumber == 2:
        return ''
    elif curveNumber == 3:
        return 'Evolution de la charge (%tb)'
    elif curveNumber == 4:
        return 'Evolution brute des fissures (Ecarts, mm)'
    elif curveNumber == 5:
        return 'Niveau piezométrique (mm)'
    else:
        return ''




