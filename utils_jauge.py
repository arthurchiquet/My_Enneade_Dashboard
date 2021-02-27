#### Import des modules dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc

#### Import des librairies python
import pandas as pd
import numpy as np
import plotly.express as px

from server import app
from config import engine
from data import get_data
from utils_maps import empty_figure

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        html.Br(),
        dbc.Container(
            [
                html.H3(
                    "Evolution brute des fissures (écarts, mm)",
                    style={"textAlign": "center"},
                ),
                dcc.Loading(
                    type="graph",
                    children=[
                        dcc.Graph(id="courbe_jauge", config={"scrollZoom": True})
                    ],
                ),
            ],
            fluid=True,
        ),
    ]
)

#### retorune la liste des jauges se trouvant dans le secteur selectionné
@app.callback(
    Output("courbe_jauge", "figure"),
    [Input("chantier-select", "data"), Input("secteur-select", "data")],
)
def update_graph_jauges(chantier, secteur_selected):

    ''' recupère la liste des jauges se trouvant dans le secteur selectioné'''

    try:
        liste_jauges = secteur_selected["jauge"]
        return graph_jauge(chantier, liste_jauges)
    except:
        return empty_figure()

#### Methode permettant de recuper la premiere valeur non nulle sur une colonne donnée
def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i

#### methode permettant de soustraire a chaque valuer d'une colonne, la premiere
#### valuer non nulle identifiée
def diff_jauge(df):
    for col in df.columns:
        df[col] = (df[col] - first(df[col])) * 100
    return df

#### Creation du graph de déplacement des jauges
def graph_jauge(chantier, jauges, height=None):

    ''' Téléchatgement des données de déplacment des jauges'''

    df = get_data(chantier, "actif", "jauge", "jauges.csv", sep=False)

    ''' Mise en forme des données'''

    df = df.rename(columns={"Date": "date"})
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    liste_colonnes = []
    for jauge in jauges:
        for col in df.columns[1:]:
            if jauge.lower() in col.lower().replace("jauge", ""):
                liste_colonnes.append(col)
    df = df.set_index("date")[liste_colonnes]
    df = diff_jauge(df)

    ''' Création du graph '''

    fig = px.line(df.reset_index(), x="date", y=df.columns, line_shape="spline")
    fig.update_layout(
        height=height,
        showlegend=False,
        yaxis_title="Ecart (mm)",
        xaxis_title=None,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 10, "t": 0, "l": 0, "b": 0},
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="grey")
    return fig
