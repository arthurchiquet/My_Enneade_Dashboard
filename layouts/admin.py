import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
import pandas as pd
from dash.dependencies import Input, Output, State
from server import app
from user_mgmt import show_users, update_profil, update_output, del_user
from chantier_mgmt import del_chantier
from config import engine
import warnings

warnings.filterwarnings("ignore")

layout = html.Div(
    [
        html.Br(),
        dbc.Container(
            [
                html.H3("Afficher utilisateurs"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dt.DataTable(
                                    id="users",
                                    columns=[
                                        {"name": "ID", "id": "id"},
                                        {"name": "Username", "id": "username"},
                                        {"name": "Email", "id": "email"},
                                        {"name": "Profil", "id": "profil"},
                                    ],
                                    data=show_users(),
                                    style_header={"backgroundColor": "rgb(30, 30, 30)"},
                                    style_cell={
                                        "backgroundColor": "rgb(50, 50, 50)",
                                        "color": "white",
                                    },
                                ),
                            ],
                            md=12,
                        ),
                    ]
                ),
            ],
            className="jumbotron",
        ),
        dbc.Container(
            [
                html.H3("Mettre à jour profil utilisateur"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Nom utilisateur: "),
                                dcc.Dropdown(
                                    id="user_list",
                                    options=update_output(),
                                    style={"width": "90%", "color": "black"},
                                ),
                                html.Br(),
                                dbc.Label("Type de profil: "),
                                dcc.Dropdown(
                                    id="profil_select",
                                    style={"width": "90%", "color": "black"},
                                    options=[
                                        {"label": "Basique", "value": 4},
                                        {"label": "Intermédiaire", "value": 3},
                                        {"label": "Complet", "value": 2},
                                    ],
                                    value=4,
                                    clearable=False,
                                ),
                                html.Br(),
                                html.Br(),
                                html.Button(
                                    children="Mettre à jour",
                                    id="update_button",
                                    n_clicks=0,
                                    type="submit",
                                    className="btn btn-alert btn-lg",
                                ),
                                html.Button(
                                    children="Supprimer",
                                    id="delete_button",
                                    n_clicks=0,
                                    type="submit",
                                    className="btn btn-alert btn-lg",
                                ),
                                html.Br(),
                                html.Div(id="update_profil_success"),
                            ],
                            md=12,
                        )
                    ]
                ),
            ],
            className="jumbotron",
        ),
        html.Br(),
        dbc.Container(
            [
                html.H3("Chantiers actifs"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dt.DataTable(
                                    id="chantiers",
                                    columns=[
                                        {"name": "Nom Chantier", "id": "nom_chantier"},
                                        {"name": "Utilisateur", "id": "username"},
                                        {"name": "Adresse", "id": "adresse"},
                                    ],
                                    data=[],
                                    style_header={"backgroundColor": "rgb(30, 30, 30)"},
                                    style_cell={
                                        "backgroundColor": "rgb(50, 50, 50)",
                                        "color": "white",
                                    },
                                ),
                            ],
                            md=12,
                        ),
                    ]
                ),
            ],
            className="jumbotron",
        ),
        html.Br(),
        dbc.Container(
            [
                html.H3("Modifier un chantier"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Nom du chantier: "),
                                dcc.Dropdown(
                                    id="chantier_list",
                                    style={"width": "90%", "color": "black"},
                                ),
                                html.Br(),
                                html.Button(
                                    children="Supprimer",
                                    id="delete_chantier",
                                    n_clicks=0,
                                    type="submit",
                                    className="btn btn-alert btn-lg",
                                ),
                                html.Br(),
                                html.Div(id="del_chantier_success"),
                            ],
                            md=12,
                        )
                    ]
                ),
            ],
            className="jumbotron",
        ),
    ]
)


@app.callback(
    Output('chantier_list', 'options'),
    Input('page-content', 'children'))
def update_choix_chantier(page):
    with engine.connect() as con:
        query = f"SELECT * FROM chantier"
        liste_chantiers = pd.read_sql_query(query, con=con).nom_chantier.tolist()
    if len(liste_chantiers)==0:
        return []
    else:
        return [{'label': chantier, 'value': chantier} for chantier in liste_chantiers]


@app.callback(
    Output("update_profil_success", "children"),
    [
        Input("update_button", "n_clicks"),
        Input("delete_button", "n_clicks"),
        Input("user_list", "value"),
        Input("profil_select", "value"),
    ],
)
def modify_profil(n_clicks1, n_clicks2, user, profil):
    if (n_clicks1 > 0) and user != "":
        update_profil(user, profil)
        return html.Div(
            children=["Le profil a été mis à jour"], className="text-success"
        )
    if (n_clicks2 > 0) and user != "":
        del_user(user)
        return html.Div(
            children=["L'utilisateur a été supprimé"], className="text-success"
        )


@app.callback(
    Output("chantiers", "data"),
    Input('page-content', 'children'))
def update_table_chantier(page):
    with engine.connect() as con:
        return pd.read_sql('chantier', con=con)[['nom_chantier', 'username', 'adresse']].to_dict('records')

@app.callback(
    Output("del_chantier_success", "children"),
    [
        Input("delete_chantier", "n_clicks"),
        Input("chantier_list", "value"),
    ],
)
def modify_chantier(n_clicks, chantier):
    if n_clicks > 0 and chantier != "":
        del_chantier(chantier)
        return html.Div(
            children=["Le chantier a bien été supprimé"], className="text-success"
        )
