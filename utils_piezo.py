import warnings
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import get_data
import pandas as pd
from config import engine
from server import app
from utils_maps import empty_figure
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data import get_data

warnings.filterwarnings("ignore")

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        dbc.Row(html.H4('Niveau piezométrique et terrassement'), justify='center'),
        dbc.Container(
            [
                dcc.Graph(
                    id="graph_piezo", figure=empty_figure(), config={"scrollZoom": True}
                ),
                html.Hr(),
                dbc.Row(html.H4('Pluviométrie (mm) et température (°C'), justify='center'),
                dcc.Graph(id="graph_meteo", figure=empty_figure()),
            ],
            fluid=True,
        )
    ]
)


@app.callback(
    Output("graph_meteo", "figure"),
    [
        Input("chantier-select", "data"),
        Input("graph_piezo", "relayoutData"),
    ],
)
def update_graph_meteo(chantier, relayout_data):
    try:
        df = get_data(chantier, "actif", "temperature.csv")
        df.Date = pd.to_datetime(df.Date, format="%d/%m/%Y")
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=["Précipitations (mm)", "Température (°C)"],
        )

        fig.add_trace(go.Scatter(name="TMIN", x=df.Date, y=df.TMIN), row=2, col=1)

        fig.add_trace(go.Scatter(name="TMAX", x=df.Date, y=df.TMAX), row=2, col=1)

        fig.add_trace(
            go.Scatter(name="Précipitations", x=df.Date, y=df.Précipitaions),
            row=1,
            col=1,
        )
        fig.update_layout(
            height=600,
            plot_bgcolor=colors["background"],
            paper_bgcolor=colors["background"],
            font_color=colors["text"],
        )
        fig.update_xaxes(showgrid=False)
        try:
            fig["layout"]["xaxis"]["range"] = [
                relayout_data["xaxis.range[0]"],
                relayout_data["xaxis.range[1]"],
            ]
            fig["layout"]["xaxis"]["autorange"] = False
        except (KeyError, TypeError):
            fig["layout"]["xaxis"]["autorange"] = True
        return fig
    except:
        return empty_figure()


@app.callback(
    Output("graph_piezo", "figure"),
    [
        Input("chantier-select", "data"),
        Input("secteur-select", "data"),
    ],
)
def update_graph_piezos(chantier, secteurselected):
    try:
        secteur = list(secteurselected.keys())[0]
        piezo = secteurselected[secteur]["piezo"][0]
        return graph_piezo(chantier, piezo, height=450)
    except:
        return empty_figure()




def graph_piezo(chantier, piezo, height=550):
    df = get_data(chantier, "actif", f"{piezo}.csv")
    terrassement = get_data(chantier, "actif", "terrassement.csv")
    df=df.rename(columns={'Date':'date'})
    terrassement=terrassement.rename(columns={'Date':'date'})
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    terrassement.date = pd.to_datetime(terrassement.date, format="%d/%m/%Y")
    with engine.connect() as con:
        query = f"select * from piezo_param WHERE nom_chantier='{chantier}' AND piezo='{piezo}'"
        params = pd.read_sql_query(query, con=con)
    Z_tete=params.Z_tête[0]
    Z_pied=params.Z_pied[0]
    unite=params.reference[0]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(name="Niveau terrassement", x=terrassement.date, y=terrassement["Coupe IJ"])
    )
    fig.add_trace(go.Scatter(name=f"Z ({unite}) pour {piezo}", x=df.date, y=df.Niveau_eau))
    fig.add_trace(go.Scatter(
        name=f"Z (Tête) {piezo} ({unite})",
        x=df.date,
        y=[Z_tete for i in range(df.shape[0])],
        mode='lines',
        line = dict(color='#7FFFD4', width=2, dash='dash')))
    fig.add_trace(go.Scatter(
        name=f"Z (Pied) {piezo} ({unite})",
        x=df.date,
        y=[Z_pied for i in range(df.shape[0])],
        mode='lines',
        line = dict(color='#DC143C', width=2, dash='dash')))
    fig.update_layout(
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin=dict(l=0, r=10, t=0, b=0),
        height=height,
        legend_orientation="h",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="grey")
    return fig
