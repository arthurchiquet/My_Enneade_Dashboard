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
from utils_maps import update_map_chantier, empty_figure
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo


warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
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
                                        config={ "scrollZoom": True},
                                        figure=empty_figure()),
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


#### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    [Input('options-store', 'data'),
    State('params-store', 'data'),
    State('map-chantier', 'figure')
    ])
def affichage_map(options, params, fig):
    data = memoized_data(options['chantier'], 'actif', 'topographie.csv')
    return update_map_chantier(fig, data, options, params)

@app.callback(
    Output('params-store', 'data'),
    Input('options-store', 'data'),
    State('params-store','data')
    )
def update_secteur(options, params):
    if params == {}:
        try:
            params = download_json(options['chantier'], 'paramètres', 'secteurs.json')
        except:
            pass
    else:
        pass
    # if selectedData is not None:
    #     if n_click >0:
    #         secteur_coords = selectedData['range']['mapbox']
    #         secteur_store[name]=secteur_coords
    #         save_json(secteur_store, chantier, 'paramètres', 'secteurs.json')
    #         return secteur_store
    # else:
    return params

@app.callback(
    Output('right-content', 'children'),
    Input("map-chantier", "clickData"))
def display_right_content(clickData):
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

##### STOCKE LA VALEUR DU SECTEUR ####

conv = {0:'Cible',1:'Inclinometre',2:'Tirant',3:'Jauge',4:'Piezometre',5:'Buton'}

### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [Output('titre_graph', 'children'),
    Output("courbe_capteur", "figure"),
    Output('sous_titre_graph', 'children')],
    [Input("map-chantier", "selectedData"),
    State('options-store', 'data')]
    )
def affichage_courbe_capteur(selectedData, options):
    # try:
    curveNumber = selectedData['points'][0]['curveNumber']
    text = selectedData['points'][0]['text']
    if curveNumber > 6 :
        return '' , empty_figure(), ''
    else:
        return f'{conv[curveNumber]} {text}', selection_affichage(options['chantier'], curveNumber, text), sous_titre(curveNumber)
    # except:
    #     return '', empty_figure(), ''


### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, curveNumber, text):
    if curveNumber == 0:
        return utils_topo.graph_topo(chantier, text, 0, height = 450, spacing=0.06)
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




