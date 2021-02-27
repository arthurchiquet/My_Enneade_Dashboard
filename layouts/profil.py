#### import des modules dash

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from flask_login import current_user
import warnings

from server import app

from user_mgmt import update_password
from werkzeug.security import check_password_hash

warnings.filterwarnings("ignore")

layout = html.Div(
    [
        html.Br(),
        dbc.Container(
            [
                html.H3("Gestion du profil"),
                html.Hr(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Nom d'utilsateur:"),
                                html.Br(),
                                html.Br(),
                                dbc.Label("Email:"),
                            ],
                            md=2,
                        ),
                        dbc.Col(
                            [
                                dbc.Label(id="username", className="text-success"),
                                html.Br(),
                                html.Br(),
                                dbc.Label(id="email", className="text-success"),
                            ],
                            md=4,
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Ancien mot de passe: "),
                                dcc.Input(
                                    id="oldPassword",
                                    type="password",
                                    className="form-control",
                                    placeholder="Saisir mot de passe",
                                    n_submit=0,
                                    style={"width": "40%"},
                                ),
                                html.Br(),
                                dbc.Label("Nouveau mot de passe: "),
                                dcc.Input(
                                    id="newPassword1",
                                    type="password",
                                    className="form-control",
                                    placeholder="Saisir mot de passe",
                                    n_submit=0,
                                    style={"width": "40%"},
                                ),
                                html.Br(),
                                dbc.Label("Confirmer nouveau mot de passe: "),
                                dcc.Input(
                                    id="newPassword2",
                                    type="password",
                                    className="form-control",
                                    placeholder="Saisir mot de passe",
                                    n_submit=0,
                                    style={"width": "40%"},
                                ),
                                html.Br(),
                                dbc.Button(
                                    id="updatePasswordButton",
                                    n_clicks=0,
                                    className="fas fa-save",
                                    size="lg",
                                ),
                                html.Br(),
                                html.Div(id="updateSuccess"),
                            ],
                            md=6,
                        ),
                    ]
                ),
            ],
            className="jumbotron",
            id="pageContent",
        ),
    ]
)


#### Affiche le nom de l'utilisateur connecté
@app.callback(
    Output("username", "children"),
    [Input("pageContent", "children")])
def currentUserName(pageContent):
    try:
        username = current_user.username
        return username
    except AttributeError:
        return ""

#### Affiche l'adresse mail de l'utilisateur connecté
@app.callback(Output("email", "children"), [Input("pageContent", "children")])
def currentUserEmail(pageContent):
    try:
        email = current_user.email
        return email
    except AttributeError:
        return ""


#### Affiche un message lors de la tentative de modification du mot de passe ( SUCCES / ERREUR)
@app.callback(
    Output("oldPassword", "className"),
    [
        Input("updatePasswordButton", "n_clicks"),
        Input("newPassword1", "n_submit"),
        Input("newPassword2", "n_submit"),
    ],
    [
        State("pageContent", "children"),
        State("oldPassword", "value"),
        State("newPassword1", "value"),
        State("newPassword2", "value"),
    ],
)
def validateOldPassword(
    n_clicks,
    newPassword1Submit,
    newPassword2Submit,
    pageContent,
    oldPassword,
    newPassword1,
    newPassword2,
):
    if (n_clicks > 0) or (newPassword1Submit > 0) or (newPassword2Submit) > 0:

        ''' check_password_hash est une fonction permettant de vérifier la correspondance
        du mot de passe (crypté) avec l'utilisateur associé'''

        if check_password_hash(current_user.password, oldPassword):
            return "form-control is-valid"
        else:
            return "form-control is-invalid"
    else:
        return "form-control"


#### Verifie que la double saisie du nouveau mot de passe est correcte
#### Affiche un message d'erreur si la premiere saisie du nouveau mot de passe est incorrecte
@app.callback(
    Output("newPassword1", "className"),
    [
        Input("updatePasswordButton", "n_clicks"),
        Input("newPassword1", "n_submit"),
        Input("newPassword2", "n_submit"),
    ],
    [State("newPassword1", "value"), State("newPassword2", "value")],
)
def validatePassword1(
    n_clicks, newPassword1Submit, newPassword2Submit, newPassword1, newPassword2
):
    if (n_clicks > 0) or (newPassword1Submit > 0) or (newPassword2Submit) > 0:
        if newPassword1 == newPassword2:
            return "form-control is-valid"
        else:
            return "form-control is-invalid"
    else:
        return "form-control"


#### Verifie que la double saisie du nouveau mot de passe est correcte
#### Affiche un message d'erreur si la deuxième saisie du nouveau mot de passe est incorrecte
@app.callback(
    Output("newPassword2", "className"),
    [
        Input("updatePasswordButton", "n_clicks"),
        Input("newPassword1", "n_submit"),
        Input("newPassword2", "n_submit"),
    ],
    [State("newPassword1", "value"), State("newPassword2", "value")],
)
def validatePassword2(
    n_clicks, newPassword1Submit, newPassword2Submit, newPassword1, newPassword2
):
    if (n_clicks > 0) or (newPassword1Submit > 0) or (newPassword2Submit) > 0:
        if newPassword1 == newPassword2:
            return "form-control is-valid"
        else:
            return "form-control is-invalid"
    else:
        return "form-control"


#### Met à jour le nouveau mot de passe dans la table SQL si l'ensemble des conditions
#### sont satisfaites
@app.callback(
    Output("updateSuccess", "children"),
    [
        Input("updatePasswordButton", "n_clicks"),
        Input("newPassword1", "n_submit"),
        Input("newPassword2", "n_submit"),
    ],
    [
        State("pageContent", "children"),
        State("oldPassword", "value"),
        State("newPassword1", "value"),
        State("newPassword2", "value"),
    ],
)
def changePassword(
    n_clicks,
    newPassword1Submit,
    newPassword2Submit,
    pageContent,
    oldPassword,
    newPassword1,
    newPassword2,
):
    if (n_clicks > 0) or (newPassword1Submit > 0) or (newPassword2Submit) > 0:
        if (
            check_password_hash(current_user.password, oldPassword)
            and newPassword1 == newPassword2
        ):
            try:
                update_password(current_user.username, newPassword1)
                return html.Div(
                    children=["Mise à jour réussie"], className="text-success"
                )
            except Exception as e:
                return html.Div(
                    children=["Echec de la mise à jour: {e}".format(e=e)],
                    className="text-danger",
                )
        else:
            return html.Div(
                children=["Ancien mot passe non valide"], className="text-danger"
            )
