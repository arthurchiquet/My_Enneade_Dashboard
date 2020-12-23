import warnings
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import get_data
import pandas as pd
from config import engine
from server import app
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from data import get_data

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}

layout = html.Div(
    [
        html.Br(),
        dbc.Container([
        dcc.Graph(id="graph_meteo", config={"scrollZoom": True}),
        html.Br(),
        dcc.Graph(id='graph_piezo')
    ], fluid=True)
    ]
)

@app.callback(
    Output("graph_meteo", "figure"),
    [
        Input("chantier-store", "data"),
    ],
)
def update_graph_meteo(chantier):
    try:
        df = get_data(chantier, 'actif', 'temperature.csv')
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
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text']
        )
        return fig
    except:
        return {}
    return fig


@app.callback(
    Output("graph_piezo", "figure"),
    [Input("chantier-store", "data"),
     Input('secteur-store', 'data'),
     Input('graph_meteo', 'relayoutData'),
     ]
    )
def update_graph_piezos(chantier, secteur, relayout_data):
    if secteur == None:
        return {}
    else:
        with engine.connect() as con:
            query=f"select * from capteur where chantier='{chantier}' and secteur ='{secteur}' and type='piezo'"
            piezo = pd.read_sql_query(query, con=con).capteur.unique()[0]
        return graph_piezo(chantier, piezo, relayout_data = relayout_data)


def graph_piezo(chantier, piezo, relayout_data = None):
    df = get_data(chantier, 'actif', f'{piezo}.csv')
    terrassement = get_data(chantier, 'actif', 'terrassement.csv')
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    terrassement.Date = pd.to_datetime(terrassement.Date, format="%d/%m/%Y")
    fig = go.Figure()
    fig.add_trace(go.Scatter(name="terrassement", x=terrassement.Date, y=terrassement['Coupe IJ']))
    fig.add_trace(go.Scatter(name="piezo", x=df.date, y=df.Niveau_eau))
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'])
    try:
        fig['layout']["xaxis"]["range"] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        fig['layout']["xaxis"]["autorange"] = False
    except (KeyError, TypeError):
        fig['layout']["xaxis"]["autorange"] = True
    return fig
