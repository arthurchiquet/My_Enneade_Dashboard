import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd
from data import download_image, get_data
import numpy as np
from datetime import timedelta

mapbox_token = "pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ"

colors = {"background": "#222222", "text": "white"}

coeff_Lamb_GPS = [[1.23952112e-05, 6.63800392e-07], [-4.81267332e-07, 8.98816386e-06]]
intercept_Lamb_GPS = [-20.17412175, 16.14120241]


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


def changement_repere(df, coef, intercept):
    lon = df.lat * coef[0][0] + df.lon * coef[0][1] + intercept[0]
    lat = df.lat * coef[1][0] + df.lon * coef[1][1] + intercept[1]
    df.lat, df.lon = lat, lon
    return df


def remove_xyz(string):
    return string[:-2]


def first(col):
    i = 0
    for j in col:
        if not np.isnan(j) & (i == 0):
            i = j
            break
    return i

def extract_position(df):
    df = df.drop(columns=["date"])
    df = pd.DataFrame(df.apply(first)).T
    dfx = (
        df[[col for col in df.columns if ".x" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "lat"})
    )
    dfy = (
        df[[col for col in df.columns if ".y" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "lon"})
    )
    dfx.cible = dfx.cible.map(remove_xyz)
    dfy.cible = dfy.cible.map(remove_xyz)
    df2 = dfx.merge(dfy)
    df2 = changement_repere(df2, coeff_Lamb_GPS, intercept_Lamb_GPS)
    return df2


#######################  AFFICHAGE MAP CHANTIER   ######################################################


def update_map_chantier(chantier, params):
    try:
        secteurs = params["secteur"]
        del params["secteur"]
    except:
        secteurs = []

    df = (
        pd.concat(
            {k: pd.DataFrame.from_dict(v, "index") for k, v in params.items()}, axis=0
        )
        .reset_index()
        .rename(columns={"level_0": "type", "level_1": "capteur"})
    )

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color="type",
        opacity=0.7,
        text="capteur",
        hover_data={"type": True},
    )

    fig.update_traces(hovertemplate="%{text}", textfont_size=11)

    fig.update_traces(
        marker=dict(size=20, color="#FF6347", opacity=0.5), selector=dict(name="inclino")
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


    for secteur in secteurs:
        coords = secteurs[secteur]
        fig.add_trace(
            go.Scattermapbox(
                name=secteur,
                mode="lines",
                text=secteur,
                lon=[
                    coords[0][0],
                    coords[0][0],
                    coords[1][0],
                    coords[1][0],
                    coords[0][0],
                ],
                lat=[
                    coords[1][1],
                    coords[0][1],
                    coords[0][1],
                    coords[1][1],
                    coords[1][1],
                ],
            )
        )
        fig.update_traces(hovertemplate="Secteur", selector={"name": secteur})

    try:
        plan = download_image(chantier, "plan.jpeg")
    except:
        plan=None

    layers = [
        dict(
            below="traces",
            minzoom=16,
            maxzoom=21,
            opacity=0.7,
            source=plan,
            sourcetype="image",
            coordinates=[
                [7.4115104, 43.7321406],
                [7.4137998, 43.7321406],
                [7.4137998, 43.7310171],
                [7.4115104, 43.7310171],
            ],
        )
    ]
    mapbox = dict(
        zoom=17.6,
        center=dict(lon=7.4126551, lat=43.7315788),
    )

    fig.update_layout(
        mapbox=mapbox,
        mapbox_style="dark",
        mapbox_accesstoken=mapbox_token,
        clickmode="event+select",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        font_family='Century Gothic, AppleGothic, sans-serif',
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
                                    "visible": [True for i in range(df.type.nunique())]
                                    + [False for i in range(len(secteurs))]
                                }
                            ],
                        ),
                        dict(
                            label="Secteurs",
                            method="update",
                            args=[
                                {
                                    "visible": [False for i in range(df.type.nunique())]
                                    + [True for i in range(len(secteurs))]
                                }
                            ],
                        ),
                        dict(
                            label="Tous",
                            method="update",
                            args=[
                                {
                                    "visible": [True for i in range(df.type.nunique())]
                                    + [True for i in range(len(secteurs))]
                                }
                            ],
                        ),
                    ]
                )
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
