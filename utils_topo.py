#### import des modules python

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

#### import des librairies python
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import zscore
import json
from math import radians, cos, sin

from config import engine
from server import app
from utils_maps import empty_figure, extract_position
from data import memoized_data


colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        dbc.Row(
            dcc.Dropdown(
                id="focus",
                style={"color": "black", "width": "150px"},
                options=[
                    {"label": "Vue chantier", "value": "chantier"},
                    {"label": "Vue secteur", "value": "secteur"},
                ],
                value="chantier",
                clearable=False,
                persistence=True,
                persistence_type="session",
            ),
            justify="center",
        ),
        html.Br(),
        dbc.Container(
            dcc.Slider(
                id="size_ref",
                min=0,
                max=1000,
                step=10,
                value=500,
                marks={
                    0: "Zoom Min.",
                    500: "50%",
                    1000: "Zoom Max.",
                },
            )
        ),
        html.Br(),
        dcc.Graph(id="graph-3D", figure=empty_figure()),
        html.Hr(),
        html.Br(),
        dbc.Row(html.H4("Dépalcement des cibles"), justify="center"),
        dbc.Row(html.H5(id="subtitle_topo"), justify="center"),
        html.Br(),
        dbc.Row(dbc.Label("Référentiel de mesure"), justify="center"),
        dbc.Row(
            dcc.Dropdown(
                id="absolu_NTZ",
                style={"color": "black", "width": "150px"},
                options=[
                    {"label": "Absolu", "value": "absolu"},
                    {"label": "Secteur", "value": "secteur"},
                ],
                value="absolu",
                clearable=False,
                persistence=True,
                persistence_type="session",
            ),
            justify="center",
        ),
        dbc.Row(dbc.Label(id="ref_ok"), justify="center"),
        html.Br(),
        dcc.Graph(id="time-series", figure=empty_figure()),
    ]
)


#### Creation du graph -> Deplacements 3D des cibles
@app.callback(
    Output("graph-3D", "figure"),
    Input("focus", "value"),
    Input("size_ref", "value"),
    State("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_graph_3D(focus, sizeref, secteur_selected, chantier):
    if secteur_selected == {}:
        return empty_figure()
    else:
        try:
            df = format_df_vector(
                memoized_data(chantier, "actif", "topographie", "topo.csv")
            )
            secteur = secteur_selected["secteur"]
            cibles = secteur_selected["cible"]
            with engine.connect() as con:
                query1 = f"SELECT * FROM cible_param where nom_chantier = '{chantier}' and masquer = 'x'"
                query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}' and nom_secteur='{secteur}'"
                secteur_params = pd.read_sql_query(query3, con=con)
                cibles_masque = pd.read_sql_query(query1, con=con).nom_capteur.tolist()
            liste_cibles = df.cible.tolist()
            for i in cibles_masque:
                try:
                    liste_cibles.remove(i)
                except ValueError:
                    pass
            df = df[df.cible.isin(liste_cibles)]
            lat1 = secteur_params.lat1[0]
            lat2 = secteur_params.lat2[0]
            lon1 = secteur_params.lon1[0]
            lon2 = secteur_params.lon2[0]
            return graph_vecteurs(df, lat1, lat2, lon1, lon2, secteur, cibles, sizeref, focus)
        except KeyError:
            return empty_figure()


@app.callback(
    Output("time-series", "figure"),
    Output("subtitle_topo", "children"),
    Output("ref_ok", "children"),
    Input("absolu_NTZ", "value"),
    Input("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_time_serie(ref, secteur_selected, chantier):
    if secteur_selected == {}:
        return empty_figure(), "", ""
    else:
        secteur = secteur_selected["secteur"]
        if ref == "secteur":
            try:
                with engine.connect() as con:
                    query = f"SELECT * FROM secteur_param WHERE nom_chantier='{chantier}' AND nom_secteur='{secteur}' "
                    angle = pd.read_sql_query(query, con=con).angle[0]
                    subtitle = "N, T, Z (mm)"
                    repere = "ntz"
            except IndexError:
                angle = 0
                subtitle = "X, Y, Z (mm)"
                repere = "xyz"

        else:
            angle = 0
            subtitle = "X, Y, Z (mm)"
            repere = "xyz"
        df = memoized_data(chantier, "actif", "topographie", "topo.csv")
        list_capteur = secteur_selected["cible"]
        with engine.connect() as con:
            query1 = f"SELECT * FROM cible_param where nom_chantier = '{chantier}' and masquer = 'x'"
            cibles_masque = pd.read_sql_query(query1, con=con).nom_capteur.tolist()
        for i in cibles_masque:
            try:
                list_capteur.remove(i)
            except ValueError:
                pass
        if angle == None:
            df = format_df(df, list_capteur, 0)
            fig = graph_topo(df, height=700)
            return fig, "Aucun référentiel renseigné pour ce secteur"
        else:
            df = format_df(df, list_capteur, angle, repere=repere)
            fig = graph_topo(df, height=700)
            return fig, subtitle, ""



def graph_vecteurs(df, lat1, lat2, lon1, lon2, nom_secteur, list_capteur, sizeref, focus):
    fig = go.Figure()
    fig.add_trace(
        go.Cone(
            x=df.x.tolist(),
            y=df.y.tolist(),
            z=df.z.tolist(),
            u=df.u.tolist(),
            v=df.v.tolist(),
            w=df.w.tolist(),
            colorscale="pinkyl",
            sizemode="absolute",
            text=df.cible,
            name="Déplacement",
            sizeref=sizeref,
        )
    )
    x1, x2, y1, y2 = changement_repere(lat1, lat2, lon1, lon2)
    z1 = df[df.cible.isin(list_capteur)].z.min()
    z2 = df[df.cible.isin(list_capteur)].z.max()
    if focus == "secteur":
        rangex = [x1, x2]
        rangey = [y1, y2]
        rangez = [z1, z2]
    else:
        rangex = None
        rangey = None
        rangez = None

        fig.add_trace(
            go.Mesh3d(
                x=[x1, x1, x2, x2, x1, x1, x2, x2],
                y=[y1, y2, y2, y1, y1, y2, y2, y1],
                z=[z1, z1, z1, z1, z2, z2, z2, z2],
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
                opacity=0.15,
                color="#FF1493",
                name=f"secteur {nom_secteur}",
            )
        )

    fig.update_layout(
        scene=dict(
            xaxis_title="Est / Ouest",
            yaxis_title="Nord / Sud",
            zaxis_title="Z",
            xaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor="white",
                mirror=True,
                range=rangex,
            ),
            yaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor="white",
                mirror=True,
                range=rangey,
            ),
            zaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor="white",
                mirror=True,
                range=rangez,
            ),
            camera=dict(eye=dict(x=0, y=-0.3, z=1.25)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=350,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )
    return fig

def graph_topo(df, height=470, memo=False, spacing=0.08, showlegend=True):
    fig = px.line(
        df,
        x="date",
        y="delta",
        facet_row="Axe",
        color="cible",
        hover_data={"cible": True},
        facet_row_spacing=spacing,
    )
    fig.update_xaxes(showgrid=False, title=dict(text=None))
    fig.update_yaxes(mirror="all", title=dict(text=None), gridcolor="grey", nticks=15)
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

def format_df(df, list_cibles, angle=0, repere="xyz"):
    df = df.rename(columns={"Date": "date"})
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
    if repere == "xyz":
        df["Axe"] = df["level_1"].map(facet_name_xyz)
    else:
        df["Axe"] = df["level_1"].map(facet_name_ntz)
    df["cible"] = df["level_1"].map(remove_xyz)
    return df.rename(columns={0: "delta"}).drop(columns="level_1")

def format_df_vector(df):
    df = df.drop(columns=["date"]).dropna(axis=1, how="all")
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    last_indexes = df.apply(pd.Series.last_valid_index).to_dict()
    first_last = {
        col: [df.loc[first_indexes[col], col], df.loc[last_indexes[col], col]]
        for col in df.columns
    }
    df = pd.DataFrame.from_dict(first_last).T.rename(columns={0: "first", 1: "last"})
    df["norm"] = df["last"] - df["first"]
    df_x = df.iloc[[3 * i for i in range(df.shape[0] // 3)], :]
    df_y = df.iloc[[3 * i + 1 for i in range(df.shape[0] // 3)], :]
    df_z = df.iloc[[3 * i + 2 for i in range(df.shape[0] // 3)], :]
    df_x = (
        df_x.reset_index()
        .rename(columns={"index": "cible", "first": "x", "norm": "u"})
        .drop(columns=["last"])
    )
    df_y = (
        df_y.reset_index()
        .rename(columns={"index": "cible", "first": "y", "norm": "v"})
        .drop(columns=["last"])
    )
    df_z = (
        df_z.reset_index()
        .rename(columns={"index": "cible", "first": "z", "norm": "w"})
        .drop(columns=["last"])
    )
    df_x.cible = df_x.cible.map(remove_xyz)
    df_y.cible = df_y.cible.map(remove_xyz)
    df_z.cible = df_z.cible.map(remove_xyz)
    df = df_x.merge(df_y).merge(df_z)
    df = df.set_index("cible")
    z_scores = zscore(df)
    abs_z_scores = np.abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    return df[filtered_entries].reset_index()


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


def changement_repere(lat1, lat2, lon1, lon2):
    coefx = [80445.63079343, -5941.61901515]
    interceptx = 1718838.64187916
    coefy = [4307.97154979, 110939.10161203]
    intercepty = -1703790.12645452
    x1 = lon1 * coefx[0] + lat1 * coefx[1] + interceptx
    x2 = lon2 * coefx[0] + lat2 * coefx[1] + interceptx
    y1 = lon1 * coefy[0] + lat1 * coefy[1] + intercepty
    y2 = lon2 * coefy[0] + lat2 * coefy[1] + intercepty
    return x1, x2, y1, y2



