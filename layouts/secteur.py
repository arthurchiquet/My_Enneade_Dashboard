import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import dash_table as dt
import warnings

from server import app
from config import engine
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

warnings.filterwarnings("ignore")

table_parametres = html.Div(
    [
        dt.DataTable(
            id="table_parametres",
            editable=True,
            filter_action="native",
            fixed_rows={"headers": True},
            style_cell={
                "backgroundColor": "rgb(50, 50, 50)",
                "color": "white",
                "textAlign": "center",
            },
            style_header={
                "backgroundColor": "rgb(20, 20, 20)",
                "color": "white",
                "fontWeight": "bold",
            },
            style_table={"height": "500px", "overflowY": "auto"},
        )
    ]
)

table_secteur = html.Div(
    [
        dt.DataTable(
            id="table_secteur",
            editable=True,
            filter_action="native",
            fixed_rows={"headers": True},
            style_cell={
                "backgroundColor": "rgb(50, 50, 50)",
                "color": "white",
                "textAlign": "center",
            },
            style_header={
                "backgroundColor": "rgb(20, 20, 20)",
                "color": "white",
                "fontWeight": "bold",
            },
            style_table={"height": "500px", "overflowY": "auto"},
        )
    ]
)

layout = html.Div(
    [
        html.Br(),
        dbc.Row(html.H4(id='secteur-title'), justify='center'),
        html.Hr(style=dict(width='400px')),
        dbc.Row(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(labelClassName="far fa-dot-circle", tab_id=1, id='topo'),
                        dbc.Tab(labelClassName="fas fa-slash", tab_id=2, id='inclino'),
                        dbc.Tab(labelClassName="fas fa-arrows-alt-h", tab_id=3, id='tirant'),
                        dbc.Tab(labelClassName="fab fa-cloudscale", tab_id=4, id='jauge'),
                        dbc.Tab(labelClassName="fas fa-water", tab_id=5, id='pizeo'),
                        # dbc.Tab(labelClassName="far fa-dot-circle", tab_id=6),
                    ],
                    id="tabs_type",
                    active_tab=1,
                    persistence=True,
                    persistence_type='session'
                ),
            ],
            justify="center",
        ),
        html.Br(),
        html.Div(id="tab_type_content"),
    ]
)


@app.callback(
    Output("secteur-title", "children"),
    Input("secteur-select", "data"),
)
def return_title(secteur_selected):
    try:
        return f'Secteur {list(secteur_selected.keys())[0]}'
    except:
        return 'Aucun secteur sélectionné'

@app.callback(
    Output("tab_type_content", "children"),
    [Input("tabs_type", "active_tab")],
    [State("chantier-select", "data"), State("secteur-select", "data")],
)
def return_tabs_content(tab, chantier, secteur):
    if tab == 1:
        return utils_topo.layout
    elif tab == 2:
        return utils_inclino.layout
    elif tab == 3:
        return utils_tirant.layout
    elif tab == 4:
        return utils_jauge.layout
    elif tab == 5:
        return utils_piezo.layout
