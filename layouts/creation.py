import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from flask_login import current_user
from utils_maps import empty_figure
import pandas as pd
import plotly.express as px
import requests
from chantier_mgmt import add_chantier

mapbox_token = "pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ"

user = "Vallicorp"

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(html.Img(src=app.get_asset_url("logo.png"), height="100px"), justify='center'),
                html.Br(),
                dbc.Row(html.H3("Définition d'un nouveau chantier"), justify="center"),
                html.Br(),
                dbc.Container(
                    [
                        dbc.Row(
                            dbc.Input(
                                id="nom_chantier",
                                placeholder="Nom du chantier",
                                style=dict(width='500px')
                            ),
                            justify="center",
                        ),
                        html.Br(),
                        dbc.Row(
                            dbc.Input(
                                id="adresse_chantier",
                                placeholder="Adresse du chantier",
                                style=dict(width='500px')
                            ),
                            justify="center",
                        ),
                        html.Br(),
                        dbc.Row(
                            [
                                dbc.Button(
                                    id="creation",
                                    className="fas fa-plus-circle mr-1",
                                    size='lg',
                                    style={'width':'80px'},
                                    n_clicks=0
                                ),
                                dbc.Button(
                                    href="/export",
                                    id='importer',
                                    className="fas fa-cloud-upload-alt mr-1",
                                    size='lg',
                                    style={'width':'80px'},
                                    disabled=True
                                ),
                            ], justify='center'
                        ),
                        html.Br(),
                        dbc.Row(html.Div(id="sucess_label", className="text-success"), justify ='center'),

                        dbc.Row(id="geo_loc", justify='center'),
                    ]
                ),
            ]
        )
    ]
)


@app.callback(
    [
        Output("geo_loc", "children"),
        Output("importer", "disabled"),
        Output("sucess_label", "children"),
    ],
    [
        Input("creation", "n_clicks"),
        State("adresse_chantier", "value"),
        State("nom_chantier", "value"),
    ],
)
def display_geoloc(n_clicks, adresse, nom):
    if n_clicks >0:
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{adresse}.json?access_token={mapbox_token}"
        response = requests.get(url).json()
        result = response["features"][0]["geometry"]["coordinates"]
        coords = {nom: result}
        add_chantier(nom, current_user.username, adresse, result[1], result[0])
        df = pd.DataFrame(coords).T.reset_index()
        fig = px.scatter_mapbox(
            df,
            lat=1,
            lon=0,
            zoom=14,
            text="index",
            height=200,
            width=700,
            hover_name="index",
        )
        fig.update_layout(mapbox_style="dark", mapbox_accesstoken=mapbox_token)
        fig.update_layout(
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_traces(marker=dict(size=30, color="#FF8C00", opacity=0.5))
        return (
            dcc.Graph(figure=fig),
           False,
            f"Le chantier {nom} a bien été créé",
        )
    else:
        return [], True, ""
