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

table_parametres = html.Div([
            dt.DataTable(
                id="table_parametres",
                editable=True,
                filter_action="native",
                fixed_rows={'headers': True},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'textAlign': 'center'
                },
                style_header={
                    'backgroundColor': 'rgb(20, 20, 20)',
                    'color': 'white',
                    "fontWeight": "bold"},
                style_table={'height': '500px', 'overflowY': 'auto'}
                    )
                ]

            )

table_secteur = html.Div([
            dt.DataTable(
                id="table_secteur",
                editable=True,
                filter_action="native",
                fixed_rows={'headers': True},
                style_cell={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white',
                    'textAlign': 'center'
                },
                style_header={
                    'backgroundColor': 'rgb(20, 20, 20)',
                    'color': 'white',
                    "fontWeight": "bold"},
                style_table={'height': '500px', 'overflowY': 'auto'}
                    )
                ]

            )


collapse_secteur = html.Div(
    [
        dbc.Row(
            dbc.Button(
                'Paramètres secteur',
                id="collapse-secteur",
                className="mb-3",
                color="dark",
            ), justify='center'
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([table_secteur])),
            id="card-secteur",
        )
    ]
)

layout=html.Div(
    [
        html.Br(),
        collapse_secteur,
        html.Br(),
        dbc.Row(
            [
                dbc.Tabs(
                    [
                        dbc.Tab(label="Cibles", tab_id=1),
                        dbc.Tab(label="Inclinomètres", tab_id=2),
                        dbc.Tab(label="Tirants", tab_id=3),
                        dbc.Tab(label="Piezometres", tab_id=5),
                        dbc.Tab(label="Jauges", tab_id=4),
                        dbc.Tab(label="Butons", tab_id=6),
                    ],
                    id="tabs_type",
                    active_tab="tab-topo",
                )
            ], justify='center'
        ),
        html.Br(),
        html.Div(id='tab_type_content')
    ]
)


collapse_type = html.Div(
    [
        dbc.Row(
            dbc.Button(
                "Afficher les paramètres",
                id="collapse-type",
                # className="mb-3",
                style={'fontColor':'white'},
            ), justify='center'
        ),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([table_parametres])),
            id="card-type",
        )
    ]
)


@app.callback(
    Output("card-type", "is_open"),
    [Input("collapse-type", "n_clicks")],
    [State("card-type", "is_open")],
)
def collapse_parametres(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    Output("card-secteur", "is_open"),
    [Input("collapse-secteur", "n_clicks")],
    [State("card-secteur", "is_open")],
)
def collapse_secteur(n, is_open):
    if n:
        return not is_open
    return is_open

# @app.callback(
#     [
#         Output("table_parametres", "data"),
#         Output("table_parametres", "columns"),
#         ],
#     [
#         Input("chantier-store", "data"),
#         Input("secteur-store", "data"),
#         Input("tabs_secteurs", "active_tab"),
#         ]
# )
# def update_table_parametres(chantier, secteur, tab):
#     df = get_data(chantier, 'paramètres', 'parametres_generaux.csv', sep=False)
#     params = df[(df.chantier==chantier) & (df.secteur==secteur)]
#     with engine.connect() as con:
#         query=f"select * from capteur where chantier='{chantier}' and secteur='{secteur}'"
#         params = pd.read_sql_query(query, con=con)
#         if tab == 1:
#             filtre_secteur = tuple(params[params.type=='cible'].capteur)
#             query=f'select * from cible_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#         if tab == 2:
#             filtre_secteur = tuple(params[params.type=='inclino'].capteur)
#             query=f'select * from inclino_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#         if tab == 3:
#             filtre_secteur = tuple(params[params.type=='tirant'].capteur)
#             query=f'select * from tirant_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#         if tab == 5:
#             filtre_secteur = tuple(params[params.type=='piezo'].capteur)
#             query=f'select * from piezo_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#         if tab == 4:
#             filtre_secteur = tuple(params[params.type=='jauge'].capteur)
#             query=f'select * from jauge_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#         if tab == 6:
#             filtre_secteur = tuple(params[params.type=='buton'].capteur)
#             query=f'select * from buton_param where cible in {filtre_secteur}'
#             parametres = pd.read_sql_query(query, con=con)
#     return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]

@app.callback(
    Output('tab_type_content', 'children'),
    [Input('tabs_type', 'active_tab')],
    [State('chantier-select', 'data'),
    State('secteur-select', 'data')])
def return_tabs_content(tab, chantier, secteur):
    if tab == 1:
        return collapse_type, html.Br(), utils_topo.layout
    elif tab == 2:
        return collapse_type, html.Br(), utils_inclino.layout
    elif tab == 3:
        return collapse_type, html.Br(), utils_tirant.layout
    elif tab == 4:
        return collapse_type, html.Br(), utils_jauge.layout
    elif tab == 5:
        return collapse_type, html.Br(), utils_piezo.layout
