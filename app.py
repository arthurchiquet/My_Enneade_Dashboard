import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from server import app
from flask_login import logout_user, current_user
from layouts import admin,conditions,error,login,login_fd,logout,profil,home,chantier,parametres, secteur,export,creation

user_profil=1

app.layout = html.Div(
    [
        dcc.Store(id='chantier-select', data={}, storage_type='session'),
        dcc.Store(id='secteur-select', data={}, storage_type='session'),
        dcc.Store(id='global-params', data={}, storage_type='session'),
        dcc.Store(id='provis-params', data={}, storage_type='session'),
        dcc.Location(id="url", refresh=False),
        html.Div(id='navBar'),
        html.Div(id="page-content")
        ]
)

# @app.callback(
#     Output("page-content", "children"),
#     Input("url", "pathname")
#     )
# def display_page(pathname):
#     if pathname == "/":
#         return home.layout
#     elif pathname == "/creation":
#         return creation.layout
#     elif pathname == "/home":
#         return home.layout
#     elif pathname == "/chantier":
#         return chantier.layout
#     elif pathname == "/secteur":
#         return secteur.layout
#     elif pathname == "/export":
#         return export.layout
#     elif pathname == "/parametres":
#         return parametres.layout
#     elif pathname == "/admin":
#         return admin.layout
#     elif pathname == "/profil":
#         return profil.layout
#     elif pathname == "/conditions":
#         return conditions.layout
#     elif pathname == "/logout":
#         return logout.layout
#     else:
#         return error.layout


PLOTLY_LOGO = "https://static.thenounproject.com/png/17592-200.png"


@app.callback(
    Output("navBar", "children"),
    [Input("page-content", "children"),
    Input("url", "pathname")])
def navBar(input1, url):
    if url == '/' or url == '/creation' or url == '/logout' or url == '/login_fd':
        return []
    else:
        # if current_user.is_authenticated:
        if True:
            # if current_user.profil == 1:
            if user_profil==1:
                navBarContents = [
                    dbc.Row(
                        id='options-buttons',
                        children=[
                            html.A(html.Img(src=PLOTLY_LOGO, height="30px"), href='/'),
                            dbc.Button('Chantier', color = 'dark', className="mr-1", href='/chantier'),
                            dbc.Button('Paramètres', color = 'dark', className="mr-1", href='/parametres'),
                            dbc.Button('Exporter', color = 'dark', className="mr-1", href='/export'),
                            dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                            dbc.Button('Admin', id= 'profil', color='dark', className="mr-1", href='admin'),
                            dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')
                        ],
                    )
                ]
            else:
                navBarContents = [
                    dbc.Row(
                        id='options-buttons',
                        children=[
                            html.A(html.Img(src=PLOTLY_LOGO, height="30px"), href='/'),
                            html.A(html.Img(src=app.get_asset_url('chantier.webp'), height="30px"),href='/chantier'),
                            html.A(html.Img(src=app.get_asset_url('import.png'), height="30px"),href='/export'),
                            html.A(html.Img(src=app.get_asset_url('profil.png'), height="30px"),href='/profil'),
                            html.A(html.Img(src=app.get_asset_url('logout.png'), height="30px"),href='/logout'),
                        ]
                    )
                ]
            return dbc.NavbarSimple(
                    children=navBarContents,
                    color='dark',
                    dark=True,
                    style=dict(height=50),
                    fluid=True
                )
        else:
            return []

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
    )
def display_page(pathname):
    if pathname == "/":
        if current_user.is_authenticated:
            if current_user.profil == 4:
                return html.H3("La page demandée est inaccessible")
            else:
                return home.layout
        else:
            return login.layout
    elif pathname == "/home":
        if current_user.is_authenticated:
            return home.layout
        else:
            return login_fd.layout
    elif pathname == "/creation":
        if current_user.is_authenticated:
            return creation.layout
        else:
            return login_fd.layout
    elif pathname == "/chantier":
        if current_user.is_authenticated:
            return chantier.layout
        else:
            return login_fd.layout
    elif pathname == "/secteur":
        if current_user.is_authenticated:
            return secteur.layout
        else:
            return login_fd.layout
    elif pathname == "/parametres":
        if current_user.is_authenticated:
            return parametres.layout
        else:
            return login_fd.layout
    elif pathname == "/export":
        if current_user.is_authenticated:
            return export.layout
        else:
            return login_fd.layout
    elif pathname == "/admin":
        if current_user.is_authenticated:
            if current_user.profil == 1:
                return admin.layout
            else:
                return html.H3("La page demandée est inaccessible")
        else:
            return login_fd.layout
    elif pathname == "/profil":
        if current_user.is_authenticated:
            return profil.layout
        else:
            return login_fd.layout
    elif pathname == "/conditions":
        return conditions.layout
    elif pathname == "/logout":
        if current_user.is_authenticated:
            logout_user()
            return logout.layout
        else:
            return logout.layout
    else:
        return error.layout

if __name__ == "__main__":
    app.run_server(debug=True)

