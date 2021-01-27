import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
import dash_table as dt
from flask_login import current_user
from data import get_data, download_json
import plotly.express as px
from config import engine
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

user = "Vallicorp"
mapbox_token = "pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ"

colors = {"background": "#222222", "text": "#FF8C00"}

layout = html.Div(
    [
        html.Div(id="map-geo"),
        html.Br(),
        dbc.Row(
            dbc.Button("+", href="/creation", size="lg", id='add_button'),
            justify="center",
        ),
        dbc.Tooltip(
            "Définir un nouveau chantier",
            target="add_button",
            placement='right'
        )
    ]
)


@app.callback(
    Output("map-geo", "children"),
    Input("page-content", "children"))
def display_map_geo(page_content):
    with engine.connect() as con:
        query = f"SELECT * FROM chantier where username = '{current_user.username}'"
        df = pd.read_sql_query(query, con=con)

    if df.shape[0]==0:
        return []
    else:
        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="nom_chantier",
            hover_data={
                "lat": False,
                "lon": False,
            },
            color_discrete_sequence=["#FF8C00"],
            height=650,
            zoom=4,
        )
        fig.update_layout(mapbox_style="dark", mapbox_accesstoken=mapbox_token)
        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            margin=dict(l=0, r=0, t=10, b=0),
        )

        return dcc.Graph(
            id="map-geo", config={"displayModeBar": False}, figure=fig)

##### SELECTIONNE CHANTIER #####
@app.callback(
    Output("chantier-select", "data"),
    Output("url", "pathname"),
    Input("map-geo", "clickData"),
)
def store_chantier(clickData):
    try:
        chantier = clickData["points"][0]["hovertext"]
        return chantier, "/chantier"
    except:
        return {}, "/"
