# Dash configuration
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from server import app

# Create app layout
layout = dbc.Container(
    [
        html.Br(),
        dbc.Container(
            [
                dcc.Location(id="url_login_df", refresh=True),
                html.Div(
                    [
                        dbc.Container(html.H3("Utilisateur non connecté")),
                        dbc.Container(
                            id="loginType",
                            children=[
                                html.Br(),
                                dbc.Button(
                                    id="back-button",
                                    n_clicks=0,
                                    className="fas fa-sign-in-alt",
                                    size="lg",
                                ),
                                html.Br(),
                            ],
                            className="form-group",
                        ),
                    ]
                ),
            ],
            className="jumbotron",
        ),
    ]
)


# Create callbacks
@app.callback(Output("url_login_df", "pathname"), [Input("back-button", "n_clicks")])
def logout_dashboard(n_clicks):
    if n_clicks > 0:
        return "/"
