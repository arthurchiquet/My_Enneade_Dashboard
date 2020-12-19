import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import dash_table as dt
from flask_login import current_user
from utils_maps import affichage_map_geo
from config import engine
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

profil=1

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}


layout = html.Div(
    [
        dcc.Store(id='chantier-store', storage_type='session'),
        html.Br(),
        dbc.Row(
            id='options-buttons',
            children=[],
            justify='center'
        ),
        dbc.Container(
            id='zone-map',
            children=[
            dcc.Loading(
                id = "loading-map",
                color='#FF8C00',
                type="cube",
                children = dcc.Graph(id='map-geo', config={'displayModeBar': False}, figure=affichage_map_geo())
                )
            ], fluid=True
        ),
        dbc.Container(
            dt.DataTable(
                id="table_param_chantier",
                editable=True,
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
                ],
                style_header = {'display': 'none'},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'minWidth': '180px',
                    'width': '180px',
                    'maxWidth': '180px',
                    'textAlign': 'center'
                    },
                ),
        )
    ]
)

@app.callback(
    [Output('chantier-store', 'data'),
    Output('url', 'pathname')],
    Input('map-geo', 'clickData'))
def click(clickData):
    try:
        return clickData['points'][0]['hovertext'], '/chantier'
    except:
        return None, '/'

@app.callback(
    Output("table_param_chantier", "data"),
    Output("table_param_chantier", "columns"),
    Input("map-geo", "hoverData"),
)
def update_table_chantier(hoverData):
    try:
        chantier = hoverData["points"][0]['hovertext']
        with engine.connect() as con:
            query="select * from chantier where nom_chantier='%s'"%chantier
            parametres = pd.read_sql_query(query, con=con)
        return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]
    except:
        return [],[]

@app.callback(
    Output('options-buttons','children'),
    Input('page-content', 'children'))
def options_buttons(content):
    if profil==1:
        return [
                dbc.Button('Profil', id= 'profil', color='link', href='profil'),
                dbc.Button('Admin', id= 'profil', color='link', href='admin'),
                dbc.Button('Déconnexion', id='logout', color='link', href='/logout')]
    else :
        return [
                dbc.Button('Profil', id= 'profil', color='link', href='profil'),
                dbc.Button('Déconnexion', id='logout', color='link', href='/logout')]
