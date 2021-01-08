import pandas as pd
import numpy as np
import plotly.express as px
import warnings
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from config import engine
from data import get_data

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': 'white'
}

layout = dbc.Container([
        dcc.Loading(
            type='graph',
            children = [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H3('Evolution de la charge des tirants (kN)', style={"textAlign": "center"}),
                                dcc.Graph(id="evol_tirants_kn", config={"scrollZoom": True}),
                            ],
                        ),
                        dbc.Col(
                            [
                                html.H3('Evolution de la charge des tirants (%tb)', style={"textAlign": "center"}),
                                dcc.Graph(id="evol_tirants%", config={"scrollZoom": True}),
                            ]
                        )
                    ]
                )
            ]
        )
    ], fluid=True
)

@app.callback(
    [
        Output("evol_tirants_kn", "figure"),
        Output("evol_tirants%", "figure"),
    ],
    [
        Input("secteur-store", "data"),
        Input("chantier-store", "data")
    ]
)
def update_graph_tirants(secteur, chantier):
    with engine.connect() as con:
        query=f"select * from capteur where chantier='{chantier}' and secteur ='{secteur}' and type='tirant'"
        liste_tirants = pd.read_sql_query(query, con=con).capteur.unique()
    return graph_tirant(chantier, liste_tirants)


def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i

def tension_blocage(df):
    df1 = df.copy()
    for col in df1.columns:
        df1[col] = df1[col] / first(df1[col])
    return df1


def format_df(df, list_tirants):
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    df = pd.DataFrame(df.set_index("date")[list_tirants])
    df_ratio = tension_blocage(df)*100
    return df, df_ratio


def graph_tirant(chantier, list_tirants, height=500, mode=1):
    df = get_data(chantier, 'actif', 'tirants.csv', sep=False)
    df, df_ratio = format_df(df, list_tirants)
    fig1 = px.line(df.reset_index(), x='date', y=list_tirants)
    fig2 = px.line(df_ratio.reset_index(), x='date', y=list_tirants)
    fig1.update_layout(
        height=height,
        legend_title_text=None,
        yaxis_title="Tension (kN)",
        xaxis_title=None,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])
    fig2.update_layout(
        height=height,
        legend_title_text=None,
        yaxis_title="Tension (%)",
        xaxis_title=None,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],)
    fig1.update_xaxes(showgrid=False)
    fig2.update_xaxes(showgrid=False)
    fig1.update_yaxes(gridcolor='grey')
    fig2.update_yaxes(gridcolor='grey')
    if mode==1:
        return fig1, fig2
    else:
        return fig2
