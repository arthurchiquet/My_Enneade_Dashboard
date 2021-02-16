import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd
from data import download_image, memoized_data
import numpy as np
from datetime import timedelta

mapbox_token = "pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ"

colors = {"background": "#222222", "text": "white"}

#######################  AFFICHAGE MAP CHANTIER   ######################################################

def update_map_chantier(chantier):

    with engine.connect() as con:
        query1 = f"SELECT * FROM chantier where nom_chantier = '{chantier}'"
        query2 = f"SELECT * FROM capteur where nom_chantier = '{chantier}'"
        query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}'"
        coord_chantier = pd.read_sql_query(query1, con=con)
        coord_capteurs = pd.read_sql_query(query2, con=con)
        coord_secteurs = pd.read_sql_query(query3, con=con)

    fig = go.Figure()

    fig.add_trace(
        go.Scattermapbox(
            name=chantier,
            mode="markers+text",
            lon=coord_chantier.lon,
            lat=coord_chantier.lat,
            text=coord_chantier.nom_chantier,
            opacity=0.3,
        )
    )

    try:
        data = memoized_data(chantier, "actif", "topographie", "topo.csv")
        visible = [True, True]
        no_visible = [True, False]
        df = extract_position(data)
        fig.add_trace(
            go.Scattermapbox(
                name="cible",
                mode="markers+text",
                lon=df.lon,
                lat=df.lat,
                text=df.cible,
                customdata=["cible" for i in range(df.shape[0])],
            )
        )
    except:
        visible = [True]
        no_visible = [True]

    for i in coord_capteurs.type.unique():
        fig.add_trace(
            go.Scattermapbox(
                name=i,
                mode="markers+text",
                customdata=[
                    i for j in range(coord_capteurs[coord_capteurs.type == i].shape[0])
                ],
                text=coord_capteurs[coord_capteurs.type == i].nom_capteur,
                lon=coord_capteurs[coord_capteurs.type == i].lon,
                lat=coord_capteurs[coord_capteurs.type == i].lat,
            )
        )

    fig.update_traces(hovertemplate="%{text}", textfont_size=11)

    fig.update_traces(
        marker=dict(size=5, color="#6495ED", opacity=1), selector=dict(name="cible")
    )

    fig.update_traces(
        marker=dict(size=20, color="#FF6347", opacity=0.5),
        selector=dict(name="inclino"),
    )
    fig.update_traces(
        marker=dict(size=20, color="#FF8C00", opacity=0.5), selector=dict(name="tirant")
    )
    fig.update_traces(
        marker=dict(size=20, color="#7CFC00", opacity=0.5), selector=dict(name="piezo")
    )
    fig.update_traces(
        marker=dict(size=20, color="#9370DB", opacity=0.5), selector=dict(name="button")
    )

    for secteur in coord_secteurs.nom_secteur:
        lat1 = coord_secteurs.lat1[0]
        lat2 = coord_secteurs.lat2[0]
        lon1 = coord_secteurs.lon1[0]
        lon2 = coord_secteurs.lon2[0]
        fig.add_trace(
            go.Scattermapbox(
                name=secteur,
                mode="lines",
                text=secteur,
                lon=[
                    lon1,
                    lon1,
                    lon2,
                    lon2,
                    lon1,
                ],
                lat=[
                    lat2,
                    lat1,
                    lat1,
                    lat2,
                    lat2,
                ],
            )
        )
        fig.update_traces(hovertemplate="Secteur", selector={"name": secteur})

    try:
        plan = download_image(chantier, "plan.jpeg")
        with engine.connect() as con:
            query = f"SELECT * FROM chantier WHERE nom_chantier='{chantier}'"
            dim = pd.read_sql_query(query, con=con)[["x1", "x2", "y1", "y2"]]
        layers = [
            dict(
                below="traces",
                minzoom=16,
                maxzoom=21,
                opacity=0.7,
                source=plan,
                sourcetype="image",
                coordinates=[
                    [dim.x1[0], dim.y2[0]],
                    [dim.x2[0], dim.y2[0]],
                    [dim.x2[0], dim.y1[0]],
                    [dim.x1[0], dim.y1[0]],
                ],
            )
        ]
    except:
        plan = None
        layers = None

    mapbox = dict(
        zoom=coord_chantier.zoom[0],
        center=dict(lon=coord_chantier.lon[0], lat=coord_chantier.lat[0]),
    )

    fig.update_layout(
        mapbox=mapbox,
        mapbox_style="dark",
        mapbox_accesstoken=mapbox_token,
        clickmode="event+select",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        font_family="Century Gothic, AppleGothic, sans-serif",
        font_size=12,
        margin=dict(l=20, r=10, t=0, b=0),
        height=580,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        legend_title_text=None,
        updatemenus=[
            dict(
                type="dropdown",
                direction="right",
                pad={"r": 10, "t": 0},
                showactive=False,
                x=0,
                xanchor="left",
                y=1.08,
                yanchor="top",
                buttons=list(
                    [
                        dict(
                            label="Capteurs",
                            method="update",
                            args=[
                                {
                                    "visible": visible
                                    + [
                                        True
                                        for i in range(
                                            len(coord_capteurs.type.unique())
                                        )
                                    ]
                                    + [
                                        False
                                        for i in range(len(coord_secteurs.nom_secteur))
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Secteurs",
                            method="update",
                            args=[
                                {
                                    "visible": no_visible
                                    + [
                                        False
                                        for i in range(
                                            len(coord_capteurs.type.unique())
                                        )
                                    ]
                                    + [
                                        True
                                        for i in range(len(coord_secteurs.nom_secteur))
                                    ]
                                }
                            ],
                        ),
                        dict(
                            label="Tous",
                            method="update",
                            args=[
                                {
                                    "visible": visible
                                    + [
                                        True
                                        for i in range(
                                            len(coord_capteurs.type.unique())
                                        )
                                    ]
                                    + [
                                        True
                                        for i in range(len(coord_secteurs.nom_secteur))
                                    ]
                                }
                            ],
                        ),
                    ]
                ),
            ),
            dict(
                type="dropdown",
                direction="right",
                showactive=False,
                x=0.18,
                xanchor="left",
                y=1.08,
                yanchor="top",
                buttons=list(
                    [
                        dict(
                            label="Afficher plan",
                            method="relayout",
                            args=[{"mapbox.layers": layers}],
                        ),
                        dict(
                            label="Masquer plan",
                            method="relayout",
                            args=[{"mapbox.layers": None}],
                        ),
                    ]
                ),
            ),
        ],
    )

    return fig


def empty_figure():
    fig = {
        "data": [],
        "layout": {
            "plot_bgcolor": colors["background"],
            "paper_bgcolor": colors["background"],
            "font": {"color": colors["text"]},
        },
    }
    return fig


def remove_xyz(string):
    return string[:-2]


def changement_repere(df):
    coefx = [1.23952055e-05, 6.63856015e-07]
    coefy = [-4.81328848e-07, 8.98817548e-06]
    interceptx = -20.17428687
    intercepty = 16.1412919
    lon = df.lat * coefx[0] + df.lon * coefx[1] + interceptx
    lat = df.lat * coefy[0] + df.lon * coefy[1] + intercepty
    df.lat, df.lon = lat, lon
    return df

def extract_position(df):
    df = df.drop(columns=["date"]).dropna(axis=1, how="all")
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    positions = {col: [df.loc[first_indexes[col], col]] for col in df.columns}
    df = pd.DataFrame.from_dict(positions).T
    df_x = df.iloc[[3 * i for i in range(df.shape[0] // 3)], :]
    df_y = df.iloc[[3 * i + 1 for i in range(df.shape[0] // 3)], :]
    df_x = df_x.reset_index().rename(columns={"index": "cible", 0: "lat"})
    df_y = df_y.reset_index().rename(columns={"index": "cible", 0: "lon"})
    df_x.cible = df_x.cible.map(remove_xyz)
    df_y.cible = df_y.cible.map(remove_xyz)
    df = df_x.merge(df_y)
    df = changement_repere(df)
    return df
