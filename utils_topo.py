import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from config import engine
import pandas as pd
import numpy as np
from server import app
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from math import radians, cos, sin
from data import query_data

colors = {
    'background': '#222222',
    'text': 'white'
}

layout = html.Div(
    [
        html.Br(),
        dbc.Row(html.H3('Déplacement normal, tangentiel et vertical (mm)'), justify='center'),
        dbc.Container([
            dcc.Loading(
                dcc.Graph(id="time-series"),
                type='graph'
                )
        ], fluid=True)
    ],
)


@app.callback(
    Output("time-series", "figure"),
    Input("secteur-store", "data"),
    State("chantier-store", "data"),
)
def update_timeseries(secteur, chantier):
    try:
        with engine.connect() as con:
            query1="select * from capteur where secteur ='%s' and type='cible'"%secteur
            query2="select * from secteur where secteur ='%s'"%secteur
            list_capteur = pd.read_sql_query(query1, con=con).capteur.unique()
            angle=pd.read_sql_query(query2, con= con).angle[0]
        return graph_topo(chantier, list_capteur, angle)
    except:
        return {}


def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i


def delta(df):
    for col in df.columns:
        df[col] = (df[col] - first(df[col]))*1000
    return df


def get_columns(df):
    col = [i[:-2] for i in df.columns][1:]
    return [col[i] for i in range(0, df.shape[1] - 1, 3)]


def clean_col(str):
    return str.replace("Auto-", "").replace("Manu-", "").replace("Sd-", "")


def select_columns(df, liste):
    return [col for col in df.columns if clean_col(col)[:-2] in liste]


def facet_name(string):
    if 'x' in string:
        return 'Normal'
    elif 'y' in string:
        return 'Tangent'
    elif 'z' in string:
        return 'Vertical'

def remove_xyz(string):
    return string[:-2]

def format_df(df, list_capteur, angle):
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    # range_date = [df.date.tolist()[-60], df.date.tolist()[-1]]
    list_colonnes = select_columns(df, list_capteur)
    df = df.set_index("date")[list_colonnes]
    df = delta(df)
    for i in range(df.shape[1]//3):
        norm = df.iloc[:,3*i]*cos(radians(angle)) - df.iloc[:,3*i+1]*sin(radians(angle))
        tang = df.iloc[:,3*i+1]*cos(radians(angle)) + df.iloc[:,3*i]*sin(radians(angle))
        df.iloc[:,3*i] = norm
        df.iloc[:,3*i+1] = tang
    df = df.stack().reset_index()
    df["Axe"] = df["level_1"].map(facet_name)
    df["Cible"] = df["level_1"].map(remove_xyz)
    return df.rename(columns={0: "delta"}).drop(columns="level_1")

def graph_topo(chantier, cible, angle, height = 700, memo = False, spacing = 0.08):
    df = query_data(chantier, 'actif', 'topographie.csv', sep=False, memo=memo)
    dff = format_df(df, cible, angle)
    fig = px.line(
        dff,
        x="date",
        y="delta",
        facet_row="Axe",
        color="Cible",
        facet_row_spacing=spacing,
    )
    fig.update_xaxes(showgrid=False, title=dict(text=None))
    fig.update_yaxes(mirror='allticks', title=dict(text=None))
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        showlegend=False,
        height=height,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin={"r":10,"t":10,"l":0,"b":0})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig
