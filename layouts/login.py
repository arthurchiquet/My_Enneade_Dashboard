import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from server import app, User
from flask_login import login_user
from werkzeug.security import check_password_hash

layout = dbc.Container(
    [
        html.Br(),
        dbc.Row(html.Img(src=app.get_asset_url("logo.png"), height="250px"), justify='center'),
        html.Br(),
        dbc.Container(
            [
                dcc.Location(id="url_login", refresh=True),
                html.Div(
                    [
                        dbc.Container(
                            id="loginType",
                            children=[
                                dbc.Row(
                                    dcc.Input(
                                        placeholder="Nom d'utilisateur",
                                        type="text",
                                        id="uname-box",
                                        className="form-control",
                                        n_submit=0,
                                        style=dict(width='300px')
                                    ), justify='center'
                                ),
                                html.Br(),
                                dbc.Row(
                                    dcc.Input(
                                        placeholder="Mot de passe",
                                        type="password",
                                        id="pwd-box",
                                        className="form-control",
                                        n_submit=0,
                                        style=dict(width='300px')
                                    ), justify='center'
                                ),
                                dbc.Row(dbc.Alert(id="alert"), justify='center'),
                                # html.Br(),
                                dbc.Row(
                                    dbc.Button(
                                        id='login-button',
                                        n_clicks=0,
                                        className="fas fa-sign-in-alt",
                                        size="lg",
                                        style={'width':'100px'}
                                    ), justify='center'
                                ),
                                dbc.Tooltip(
                                    "Se connecter",
                                    target="login-button",
                                    placement='down'
                                ),
                                html.Br(),
                                dbc.Row(
                                    dcc.Link(
                                        children="Créer un compte",
                                        href='/conditions'
                                    ), justify='center'
                                ),
                                html.Br(),
                            ],
                            className="form-group",
                        ),
                    ]
                ),
            ],
        ),
    ]
)


@app.callback(
    Output("url_login", "pathname"),
    [Input("login-button", "n_clicks")],
    [State("uname-box", "value"), State("pwd-box", "value")],
)
def sucess(n_click, input1, input2):
    user = User.query.filter_by(username=input1).first()
    if user:
        if check_password_hash(user.password, input2):
            login_user(user, remember=True)
            return "/home"
        else:
            pass
    else:
        pass


@app.callback(
    [Output("alert", "children"), Output("alert", "color")],
    [Input("login-button", "n_clicks")],
    [State("uname-box", "value"), State("pwd-box", "value")],
)
def update_output(n_clicks, input1, input2):
    if n_clicks > 0:
        user = User.query.filter_by(username=input1).first()
        if user:
            if check_password_hash(user.password, input2):
                return ("", None)
            else:
                return ("Identifiant ou mot de passe incorrect", "danger")
        else:
            return ("Identifiant ou mot de passe incorrect", "danger")
    else:
        return ("", None)
