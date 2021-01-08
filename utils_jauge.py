import pandas as pd
import numpy as np
import plotly.express as px
from server import app
from config import engine
from data import get_data
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc


colors = {
    'background': '#222222',
    'text': 'white'
}

layout = html.Div([
    html.Br(),
    dbc.Container([
            html.H3("Evolution brute des fissures (écarts, mm)", style={"textAlign": "center"}),
            dcc.Loading(
                type='graph',
                children = [dcc.Graph(id="courbe_jauge", config={"scrollZoom": True})]
            )
        ], fluid=True)
    ])

@app.callback(
    Output("courbe_jauge", "figure"),
    [Input("chantier-store", "data"),
     Input("secteur-store", 'data')])
def update_graph_jauges(chantier, secteur):
    try:
        with engine.connect() as con:
            query=f"select * from capteur where chantier='{chantier}' and secteur ='{secteur}' and type='jauge'"
            liste_jauges = pd.read_sql_query(query, con=con).capteur.unique()
        return graph_jauge(chantier, liste_jauges)
    except:
        return {}

def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i

def diff_jauge(df):
    for col in df.columns:
        df[col] = (df[col] / first(df[col]))*100
    return df

def format_df(df):
    df.Date = pd.to_datetime(df.Date, format="%d/%m/%Y")
    df = df.set_index("Date")
    df = diff_jauge(df)
    return df

def graph_jauge(chantier, jauge):
    df = get_data(chantier, 'actif', 'jauges.csv', sep=False)
    df = format_df(get_data(chantier, 'actif', 'jauges.csv', sep=False)[['Date',jauge]])
    fig = px.line(df.reset_index(), x="Date", y=df.columns, line_shape='spline')
    fig.update_layout(
        showlegend=False,
        yaxis_title="% Jauges",
        xaxis_title=None,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin={"r":10,"t":0,"l":0,"b":0})
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='grey')
    return fig
