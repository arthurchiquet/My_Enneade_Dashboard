import warnings
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import get_data, export_data
import pandas as pd
from server import app
from config import engine
import dash_table as dt

warnings.filterwarnings("ignore")

profil = 1

tab_content_param = dbc.Container(
    [
        html.Br(),
        dt.DataTable(
            id="table_params",
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
        ),
        html.Br(),
        dbc.Button(
            children="Mettre à jour les paramètres",
            n_clicks=0,
            id="update_params",
            color="dark",
        ),
        html.Div(
            id="update_success",
            className="text-success",
        ),
    ]
)

tabs_pram = html.Div(
    [
        html.Br(),
        dbc.Row(
            dbc.Tabs(
                [
                    dbc.Tab(label="Chantier", tab_id="tab-chantier"),
                    dbc.Tab(label="Secteur", tab_id="tab-secteur"),
                    dbc.Tab(label="Cibles", tab_id="tab-topo"),
                    dbc.Tab(label="Inclinomètres", tab_id="tab-inclino"),
                    dbc.Tab(label="Tirants", tab_id="tab-tirant"),
                    dbc.Tab(label="Piezometres", tab_id="tab-piezo"),
                    dbc.Tab(label="Jauges", tab_id="tab-jauge"),
                    dbc.Tab(label="Butons", tab_id="tab-buton"),
                ],
                id="tabs_param",
                active_tab="tab-chantier",
            ),
            justify="center",
        ),
        tab_content_param,
    ]
)

layout = tabs_pram


@app.callback(
    [
        Output("table_params", "data"),
        Output("table_params", "columns"),
    ],
    [
        Input("chantier-select", "data"),
        Input("secteur-select", "data"),
        Input("tabs_param", "active_tab"),
    ],
)
def update_table(chantier, secteur, tab):
    df = get_data(chantier, "paramètres", "parametres_generaux.csv", sep=False)
    params = df[(df.chantier == chantier) & (df.secteur == secteur)]
    if tab == "tab-chantier":
        parametres = []
    if tab == "tab-secteur":
        query = f"select * from secteur where chantier='{chantier}' and secteur='{secteur}'"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-topo":
        filtre_secteur = tuple(params[params.type == "cible"].capteur)
        query = f"select * from cible_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-inclino":
        filtre_secteur = tuple(params[params.type == "inclino"].capteur)
        query = f"select * from inclino_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-tirant":
        filtre_secteur = tuple(params[params.type == "tirant"].capteur)
        query = f"select * from tirant_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-piezo":
        filtre_secteur = tuple(params[params.type == "piezo"].capteur)
        query = f"select * from piezo_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-jauge":
        filtre_secteur = tuple(params[params.type == "jauge"].capteur)
        query = f"select * from jauge_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    if tab == "tab-buton":
        filtre_secteur = tuple(params[params.type == "buton"].capteur)
        query = f"select * from buton_param where cible in {filtre_secteur}"
        parametres = pd.read_sql_query(query, con=con)
    return parametres.to_dict("records"), [
        {"name": i, "id": i} for i in parametres.columns
    ]


@app.callback(
    Output("update_success", "children"),
    [
        Input("table_params", "data"),
        Input("update_params", "n_clicks"),
        Input("chantier-select", "data"),
    ],
)
def update_params(data, n_clicks, chantier):
    if n_clicks > 0:
        df = pd.DataFrame(data)
        export_data(df, chantier, "paramètres", "parametres_generaux.csv")
        return "Les paramètres ont bien été sauvegardés"
    else:
        return ""
