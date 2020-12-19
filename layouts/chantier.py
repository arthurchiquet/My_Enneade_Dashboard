import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from utils_maps import affichage_map_chantier
import warnings
profil=1

warnings.filterwarnings("ignore")

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}


layout = html.Div(
    children=[
        html.Br(),
        dbc.Label(id='capteur'),
        dbc.Row(
            children=[dbc.Button('Carte', id='back-map', className="mr-1", href='/')],
            justify='center'
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Container(
                        children=[
                        dcc.Loading(
                            id = "loading-map",
                            color='#FF8C00',
                            type="cube",
                            children = dcc.Graph(id='map-chantier', config={'displayModeBar': False, "scrollZoom": True})
                            )
                        ], fluid=True
                    )
                ),
                dbc.Col(
                    dbc.Container(
                        children=[
                        dcc.Loading(
                            id = "loading-graph",
                            color='#FF8C00',
                            type="cube",
                            children = dcc.Graph(id='courbe_capteur', config={'displayModeBar': False, "scrollZoom": True})
                            )
                        ], fluid=True
                    )
                ),
            ]
        )
    ]
)

@app.callback(
    Output("map-chantier", "figure"),
    Input('chantier-store', 'data'))
def affichage_map(chantier_store):
    return affichage_map_chantier(chantier_store)
