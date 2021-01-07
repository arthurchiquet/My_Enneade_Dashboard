import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from server import app
from flask_login import logout_user, current_user
from layouts import admin,conditions,error,login,login_fd,logout,profil,home,chantier,parametres



app.layout = html.Div(
    [
        dcc.Store(id='chantier-store', storage_type='session'),
        dcc.Store(id='secteur-store', storage_type='session'),
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
        ]
)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
    )
def display_page(pathname):
    if pathname == "/":
        return home.layout
    elif pathname == "/home":
        return home.layout
    elif pathname == "/chantier":
        return chantier.layout
    elif pathname == "/parametres":
        return parametres.layout
    elif pathname == "/admin":
        return admin.layout
    elif pathname == "/profil":
        return profil.layout
    elif pathname == "/conditions":
        return conditions.layout
    elif pathname == "/logout":
        return logout.layout
    else:
        return error.layout

if __name__ == "__main__":
    app.run_server(debug=True)



# @app.callback(
#     Output("page-content", "children"),
#     Input("url", "pathname")
#     )
# def display_page(pathname):
#     if pathname == "/":
#         if current_user.is_authenticated:
#             if current_user.profil == 4:
#                 return html.H3("La page demandée est inaccessible")
#             else:
#                 return home.layout
#         else:
#             return login.layout
#     elif pathname == "/home":
#         if current_user.is_authenticated:
#             return home.layout
#         else:
#             return login_fd.layout
#     elif pathname == "/admin":
#         if current_user.is_authenticated:
#             if current_user.profil == 1:
#                 return admin.layout
#             else:
#                 return html.H3("La page demandée est inaccessible")
#         else:
#             return login_fd.layout
#     elif pathname == "/profil":
#         if current_user.is_authenticated:
#             return profil.layout
#         else:
#             return login_fd.layout
#     elif pathname == "/conditions":
#         return conditions.layout
#     elif pathname == "/logout":
#         if current_user.is_authenticated:
#             logout_user()
#             return logout.layout
#         else:
#             return logout.layout
#     else:
#         return error.layout



