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
from data import get_data, save_json, download_json, memoized_data
from utils_maps import update_map_chantier, empty_figure, extract_position
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo
import json

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
                                    dcc.Graph(
                                        id='map-chantier',
                                        config={ "scrollZoom": True, 'modeBarButtonsToRemove':['lasso2d']},
                                        figure=empty_figure()),
                                    html.Pre(id='hover-data', style=styles['pre']),
                                    dbc.Row(
                                        [
                                            dbc.RadioItems(
                                                options=[
                                                    {"label": "Contrôler carte", "value": 1},
                                                    {"label": "Ajouter / Modifier", "value": 2},
                                                    {"label": "Selectionner un secteur", "value": 3},
                                                ],
                                                value=1,
                                                id="options-map",
                                                inline=True,
                                            ),
                                        ]
                                            , justify='center'
                                    ),
                                    dbc.Row(id='button-secteur')
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
        )
    ]
)

@app.callback(
    Output('hover-data', 'children'),
    Input('map-chantier', 'clickData'))
def display_hover_data(hoverData):
    return json.dumps(hoverData, indent=2)

#### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('chantier-select', 'data'),
    Input('secteurs-params', 'data'),
    State('capteurs-params', 'data'),
    # State('map-chantier', 'figure')
    ])
def affichage_map(chantier, secteurs, capteurs):
    return update_map_chantier(chantier, secteurs, capteurs)

@app.callback(
    Output('secteurs-params', 'data'),
    Output('capteurs-params', 'data'),
    Input('chantier-select', 'data'),
    # State('secteurs-params','data'),
    # State('capteurs-params','data')
    )
def update_params(chantier):
    if chantier == {}:
        return {}, {}
    else:
        secteurs = download_json(chantier, 'paramètres', 'secteurs.json')
        capteurs_sup = download_json(chantier, 'paramètres', 'capteurs.json')
        data = memoized_data(chantier, 'actif', 'topographie.csv')
        data_positions = extract_position(data).set_index('cible')
        capteurs = {'cible' : data_positions.to_dict('index')}
        capteurs.update(capteurs_sup)
        return secteurs, capteurs


# @app.callback(
#     Output('secteur-select', 'data'),
#     Input('map-chantier', 'clickData'),
#     State('secteurs-params', 'data'),
#     State('capteurs-params', 'data')
#     # State('button','n_clicks'),
#     )
# def select_secteur(selection, secteurs_params, capteurs_params):

#     secteur = secteurs_params[selection]
#     df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for k, v in capteurs_params.items()},axis=0).reset_index().rename(columns={'level_0':'type','level_1':'capteur'})
#     capteurs = df[(df.lon > s[0][0]) & (df.lon < s[1][0]) & (df.lat < s[0][1]) &(df.lat > s[1][1])]
#     return {secteur: {t: capteurs[capteurs['type']==t]['capteur'].tolist() for t in capteurs['type'].unique()}}



@app.callback(
    Output('right-content', 'children'),
    [Input('options-map', 'value'),
    Input("map-chantier", "clickData")])
def display_right_content(option, clickData):
    if option == 1:
        if clickData:
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
        else:
            return []
    elif option == 2:
        return [
            # dbc.Row()
            dbc.Row(
                dcc.Dropdown(
                    id="type_modif",
                    style={"width": "50%", 'color':'black'},
                    options=[
                        {"label": "Secteur", "value": 1},
                        {"label": "Sous-secteur", "value": 2},
                        {"label": "Inclinomètre", "value": 3},
                        {"label": "Tirant", "value": 4},
                        {"label": "Jauge", "value": 5},
                        {"label": "Piezomètre", "value": 6},
                    ],
                    clearable=False,
                ), justify='center'
            )
        ]

    elif option == 3:
        return [

        ]

### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [Output('titre_graph', 'children'),
    Output("courbe_capteur", "figure"),
    Output('sous_titre_graph', 'children')],
    [Input("map-chantier", "selectedData"),
    State('chantier-select', 'data')]
    )
def affichage_courbe_capteur(selectedData, chantier):
    try:
        customdata = selectedData['points'][0]['customdata'][0]
        text = selectedData['points'][0]['text']
        return f'{customdata} {text}', selection_affichage(chantier, customdata, text), sous_titre(customdata)
    except:
        return '', empty_figure(), ''


### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, text):
    if customdata == 'cible':
        return utils_topo.graph_topo(chantier, text, 0, height = 550, spacing=0.06)
    elif customdata == 'inclino':
        return utils_inclino.graph_inclino(chantier, text)
    elif customdata == 'tirant':
        return utils_tirant.graph_tirant(chantier, text, height = 550, mode=2)
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




