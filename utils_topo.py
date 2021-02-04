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
from utils_maps import empty_figure
from math import radians, cos, sin
from data import memoized_data

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Row(
                    html.H4("Positions des cibles sélectionnées"), justify="center"
                ),
                dbc.Row(
                    [dcc.Loading(dcc.Graph(id="3d-positions"), type="graph")], justify='center'
                ),
            ], width=5),
            dbc.Col([
                dbc.Row(
                    html.H4("Déplacement normal, tangentiel et vertical (mm)"), justify="center"
                ),
                dbc.Container(
                    [dcc.Loading(dcc.Graph(id="time-series"), type="graph")], fluid=True
                ),
            ], width=7)
        ])
    ]
)


@app.callback(
    Output("time-series", "figure"),
    Input("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_timeseries(secteur_selected, chantier):
    try:
        secteur = list(secteur_selected.keys())[0]
        list_capteur = secteur_selected[secteur]["cible"]
        return graph_topo(chantier, list_capteur, 0)
    except:
        return empty_figure()

@app.callback(
    Output("3d-positions", "figure"),
    Input("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_3d_graph(secteur_selected, chantier):
    try:
        secteur = list(secteur_selected.keys())[0]
        list_capteur = secteur_selected[secteur]["cible"]
        df = extract_3d_positions(chantier, list_capteur, secteur)
        return graph_3d_positions(df)
    except:
        return empty_figure()


def affect(nom_capteur, liste_capteur, nom_secteur):
    if nom_capteur in liste_capteur:
        return nom_secteur
    else:
        return 'Hors secteur'

def extract_3d_positions(chantier, liste_capteur, secteur):
    df = memoized_data(chantier, "actif", "topographie.csv")
    df = df.drop(columns=["date"])
    df = pd.DataFrame(df.apply(first)).T
    dfx = (
        df[[col for col in df.columns if ".x" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "x"})
    )
    dfy = (
        df[[col for col in df.columns if ".y" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "y"})
    )
    dfz = (
        df[[col for col in df.columns if ".z" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "z"})
    )
    dfx.cible = dfx.cible.map(remove_xyz)
    dfy.cible = dfy.cible.map(remove_xyz)
    dfz.cible = dfz.cible.map(remove_xyz)
    df2 = dfx.merge(dfy).merge(dfz)
    df2['secteur'] = df2.apply(lambda x: affect(x['cible'], liste_capteur, secteur), axis=1)
    df2 = df2[(df2.x < df2.x.mean()*1.2)&(df2.x > df2.x.mean()*0.8)&(df2.y < df2.y.mean()*1.2)&(df2.y >df2.y.mean()*0.8)&(df2.z < df2.z.mean()*1.2)&(df2.z >df2.z.mean()*0.8)]
    return df2

def graph_3d_positions(df):
    fig = px.scatter_3d(
        df,
        x='x',
        y='y',
        z='z',
        color='secteur',
        hover_data={"cible": True, 'x':False, 'y':False, 'z':False}
    )
    fig.update_traces(
        marker=dict(size=3)
    )

    fig.update_layout(
        scene=dict(
            xaxis_title="Est",
            yaxis_title="Nord",
            zaxis_title="Profondeur",
            xaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            yaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            zaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
        ),
        margin=dict(l=20, r=20, t=0, b=0),
        width=650,
        height=470,
        showlegend=False,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )
    return fig

def first(col):
    i = 0
    for j in col:
        if not np.isnan(j) & (i == 0):
            i = j
            break
    return i


def delta(df):
    for col in df.columns:
        df[col] = (df[col] - first(df[col])) * 1000
    return df


def get_columns(df):
    col = [i[:-2] for i in df.columns][1:]
    return [col[i] for i in range(0, df.shape[1] - 1, 3)]


def select_columns(df, liste):
    return [col for col in df.columns if col[:-2] in liste]


def facet_name_xyz(string):
    if "x" in string:
        return "x"
    elif "y" in string:
        return "y"
    elif "z" in string:
        return "z"

def facet_name_ntz(string):
    if "x" in string:
        return "Normal"
    elif "y" in string:
        return "Tangent"
    elif "z" in string:
        return "Vertical"


def remove_xyz(string):
    return string[:-2]


def format_df(df, list_cibles, angle, repere='xyz'):
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    liste_colonnes = select_columns(df, list_cibles)
    df = df.set_index("date")[liste_colonnes]
    df = delta(df)
    for i in range(df.shape[1] // 3):
        norm = df.iloc[:, 3 * i] * cos(radians(angle)) - df.iloc[:, 3 * i + 1] * sin(
            radians(angle)
        )
        tang = df.iloc[:, 3 * i + 1] * cos(radians(angle)) + df.iloc[:, 3 * i] * sin(
            radians(angle)
        )
        df.iloc[:, 3 * i] = norm
        df.iloc[:, 3 * i + 1] = tang
    df = df.stack().reset_index()
    if repere=='xyz':
       df["Axe"] = df["level_1"].map(facet_name_xyz)
    else:
        df["Axe"] = df["level_1"].map(facet_name_ntz)
    df["Cible"] = df["level_1"].map(remove_xyz)
    return df.rename(columns={0: "delta"}).drop(columns="level_1")


def graph_topo(
    chantier, list_cibles, angle, height=470, memo=False, spacing=0.08, showlegend=True
):
    df = memoized_data(chantier, "actif", "topographie.csv")
    dff = format_df(df, list_cibles, angle)
    fig = px.line(
        dff,
        x="date",
        y="delta",
        facet_row="Axe",
        color="Cible",
        facet_row_spacing=spacing,
    )
    fig.update_xaxes(showgrid=False, title=dict(text=None))
    fig.update_yaxes(mirror="allticks", title=dict(text=None), gridcolor="grey")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        showlegend=showlegend,
        height=height,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 10, "t": 10, "l": 0, "b": 0},
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig
