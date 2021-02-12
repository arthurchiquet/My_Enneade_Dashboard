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

coefx = [1.23952055e-05, 6.63856015e-07]
coefy = [-4.81328848e-07,  8.98817548e-06]
interceptx = -20.17428687
intercepty = 16.1412919

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


def changement_repere(df, coefx, coefy, interceptx, intercepty):
    lon = df.lat * coefx[0] + df.lon * coefx[1] + interceptx
    lat = df.lat * coefy[0] + df.lon * coefy[1] + intercepty
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
    df=df.drop(columns=["date"]).dropna(axis=1, how="all")
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    positions = {col : [df.loc[first_indexes[col], col]] for col in df.columns}
    df =pd.DataFrame.from_dict(positions).T
    df_x=df.iloc[[3*i for i in range(df.shape[0]//3)],:]
    df_y=df.iloc[[3*i+1 for i in range(df.shape[0]//3)],:]
    df_x=df_x.reset_index().rename(columns={'index':'cible',0:'lat'})
    df_y=df_y.reset_index().rename(columns={'index':'cible',0:'lon'})
    df_x.cible=df_x.cible.map(remove_xyz)
    df_y.cible=df_y.cible.map(remove_xyz)
    df=df_x.merge(df_y).set_index('cible')
    df = changement_repere(df, coefx, coefy, interceptx, intercepty)
    return df


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
        with engine.connect() as con:
            query=f"SELECT * FROM chantier WHERE nom_chantier='{chantier}'"
            dim = pd.read_sql_query(query, con=con)[['x1','x2','y1','y2']]
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
                [dim.x1[0], dim.y2[0]],
                [dim.x2[0], dim.y2[0]],
                [dim.x2[0], dim.y1[0]],
                [dim.x1[0], dim.y1[0]],
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
