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
                persistence_type="local",
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
        )
    ]
)

@app.callback(
    Output("map-chantier", "figure"),
    [Input('chantier-store', 'data'),
    Input('mode', 'value')])
def affichage_map(chantier_store, mode):
    return affichage_map_chantier(chantier_store, mode)

@app.callback(
    Output('secteur-store', 'data'),
    Input('map-chantier', 'clickData'),
    State('mode', 'value'))
def click(clickData, mode):
    try:
        return clickData['points'][0]['hovertext']
    except:
        return {}

@app.callback(
    [Output('tire_graph', 'children'),
    Output("courbe_capteur", "figure")],
    Input("map-chantier", "clickData"),
    State('chantier-store', 'data'),
    State('mode', 'value'))
def affichage_courbe_capteur(clickData, chantier, mode):
    if mode != 'GPS':
        return '', empty_figure()
    else:
        try :
            customdata = clickData['points'][0]['customdata'][0]
            hovertext = clickData['points'][0]['hovertext']
            return f'{customdata} : {hovertext}', selection_affichage(chantier, customdata, hovertext)
        except:
            return '', empty_figure()

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
