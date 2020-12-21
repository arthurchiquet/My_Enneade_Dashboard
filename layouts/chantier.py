import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import plotly.graph_objects as go
from utils_maps import affichage_map_chantier
from utils_topo import graph_topo
from utils_inclino import graph_inclino
from utils_jauge import graph_jauge
# from utils_tirant import graph_tirant
# from utils_piezo import graph_piezo
import warnings
import json


warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}

dropdowns = dcc.Dropdown(
                id='mode',
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
        dbc.Label(id='capteur'),
        dbc.Row(
            children=[dbc.Button('Carte', id='back-map', className="mr-1", href='/')],
            justify='center'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(dropdowns, justify = 'center'),
                        html.Br(),
                        dbc.Row(
                            dbc.Container(
                                children=[
                                dcc.Loading(
                                    id = "loading-map-chantier",
                                    color='#FF8C00',
                                    type="cube",
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
                ),
            ]
        )
    ]
)

@app.callback(
    Output("map-chantier", "figure"),
    Input('chantier-store', 'data'))
def affichage_map(chantier_store):
    return affichage_map_chantier(chantier_store)

@app.callback(
    [Output('tire_graph', 'children'),
    Output("courbe_capteur", "figure")],
    [Input("map-chantier", "clickData"),
    Input('chantier-store', 'data')])
def affichage_courbe_capteur(clickData, chantier):
    try :
        customdata = clickData['points'][0]['customdata'][0]
        hovertext = clickData['points'][0]['hovertext']
        return f'{customdata} : {hovertext}', selection_affichage(chantier, customdata, hovertext)
    except:
        fig = go.Figure(
            layout=dict(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background']
                )
            )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return '', fig


def selection_affichage(chantier, customdata, hovertext):
    if customdata == 'cible':
        return graph_topo(chantier, hovertext)
    elif customdata == 'inclino':
        return graph_inclino(chantier, hovertext)
    elif customdata == 'tirant':
        return graph_tirant(chantier, hovertext)
    elif customdata == 'jauge':
        return graph_jauge(chantier, hovertext)
    elif customdata == 'piezo':
        return graph_piezo(chantier, hovertext)

