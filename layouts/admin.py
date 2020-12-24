import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table as dt
from dash.dependencies import Input, Output, State
from server import app
from user_mgmt import show_users, update_profil, update_output
from config import engine
import warnings

warnings.filterwarnings("ignore")

layout = html.Div(
    [
        html.Br(),
        dbc.Row(
            justify="center",
            children = [
                dbc.Button('Accueil', id= 'accueil', className="mr-1", href='/home'),
                dbc.Button('Profil', id= 'profil', className="mr-1", href='profil'),
                dbc.Button('Déconnexion', id='logout', className="mr-1", href='/logout')]
        ),
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
                                    style_header={'backgroundColor': 'rgb(30, 30, 30)'},
                                    style_cell={
                                        'backgroundColor': 'rgb(50, 50, 50)',
                                        'color': 'white'
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
                                    style={"width": "90%", 'color':'black'},
                                ),
                                html.Br(),
                                dbc.Label("Type de profil: "),
                                dcc.Dropdown(
                                    id="profil_select",
                                    style={"width": "90%", 'color':'black'},
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
                                    className="btn btn-primary btn-lg",
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
    ],
    id="content",
)


@app.callback(
    Output("update_profil_success", "children"),
    [
        Input("update_button", "n_clicks"),
        Input("user_list", "value"),
        Input("profil_select", "value"),
    ],
)
def modify_profil(n_clicks, user_list, profil):
    if (n_clicks > 0) and user_list != "":
        update_profil(user_list, profil)
        return html.Div(
            children=["Le profil a été mis à jour"], className="text-success"
        )
