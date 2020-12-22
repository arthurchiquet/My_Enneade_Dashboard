import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import pandas as pd
from config import engine
from utils_inclino import inclino_content
from utils_topo import topo_content
from data import get_data
from server import app

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

test = html.Pre(id='click-data', style=styles['pre'])

tabs = dbc.Tabs(
    [
        dbc.Tab(test, id='tab_topo', label="Cibles"),
        dbc.Tab(inclino_content, id='tab_inclino', label="Inclinomètres"),
        dbc.Tab(id='tab_tirant', label="Tirants"),
        dbc.Tab(id='tab_piezo', label="Piezomètres"),
        dbc.Tab(id='tab_jauge', label="Jauges"),
        dbc.Tab(id='tab_buton', label="Butons"),
    ], id='tab_secteur'
)

layout = tabs


@app.callback(
    Output("time-series", "figure"),
    Input("secteur-store", "data"),
    State("chantier-store", "data"),
)
def update_timeseries(secteur, chantier):
    # try:
    with engine.connect() as con:
        query1="select * from capteur where secteur ='%s' and type=1"%secteur
        query2="select * from secteur where secteur ='%s'"%secteur
        list_capteur = pd.read_sql_query(query1, con=con).capteur.unique()
        angle=pd.read_sql_query(query2, con= con).angle[0]
    df = memoized_df(chantier, 'actif', 'topographie.csv')
    df = format_df(df, list_capteur, angle)
    return create_time_series(df)
    # except:
    #     return {}

@app.callback(
    Output('click-data', 'children'),
    Input('secteur-store', 'data'))
def display_click_data(secteur):
    return secteur
