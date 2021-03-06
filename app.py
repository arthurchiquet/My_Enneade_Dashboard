###   IMPORTATION DES MODULES

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

###   IMPORTAION DES MODULES + ENSEMBLE DES PAGES
from server import app
from flask_login import logout_user, current_user
from layouts import (
    admin,
    conditions,
    error,
    login,
    login_fd,
    logout,
    profil,
    home,
    chantier,
    parametres,
    secteur,
    export,
    creation,
    synthese,
)

user_profil = 1

app.layout = html.Div(
    [
        dcc.Store(id="chantier-select", data={}, storage_type="session"),
        dcc.Store(id="secteur-select", data={}, storage_type="session"),
        dcc.Location(id="url", refresh=False),
        html.Div(id="navBar"),
        html.Div(id="page-content"),
    ],
)


###     CREATION DES BOUTONS DE LA BARRE DE NAVIGATION EN
###     FONCTION DU PROFIL UTILISATEUR
def return_buttons(profil):
    if profil == 1:
        buttons = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-globe-europe",
                            href="home",
                            id="home",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Sélection chantier", target="home", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-layer-group mr-1",
                            href="/chantier",
                            id="menu-chantier",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Carte intéractive",
                            target="menu-chantier",
                            placement="down",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-chart-line mr-1",
                            href="/secteur",
                            id="menu-secteur",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Synthèse par secteur",
                            target="menu-secteur",
                            placement="down",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-sliders-h mr-1",
                            href="/parametres",
                            id="params",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Paramètres chantier", target="params", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-cloud-upload-alt mr-1",
                            href="/export",
                            id="export",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Importer un fichier", target="export", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            id="pdf",
                            className="fas fa-file-pdf mr-1",
                            href="/rapport",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Exporter en PDF", target="pdf", placement="down"),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-user-circle mr-1",
                            href="/profil",
                            id="profil",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Modifier le profil", target="profil", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    dbc.Button(
                        className="fas fa-users-cog mr-1",
                        href="/admin",
                        style={"height": "30px", "width": "50px"},
                    ),
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-question-circle mr-1",
                            href="/aide",
                            id="aide",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Aide", target="aide", placement="down"),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-sign-out-alt mr-1",
                            href="/logout",
                            id="logout",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Déconnexion", target="logout", placement="down"),
                    ]
                ),
            ],
            no_gutters=True,
            className="ml-auto flex-nowrap mt-3 mt-md-0",
            align="center",
        )
    else:
        buttons = dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-globe-europe",
                            href="home",
                            id="home",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Sélection chantier", target="home", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-layer-group mr-1",
                            href="/chantier",
                            id="menu-chantier",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Carte intéractive",
                            target="menu-chantier",
                            placement="down",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-chart-line mr-1",
                            href="/secteur",
                            id="menu-secteur",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Synthèse par secteur",
                            target="menu-secteur",
                            placement="down",
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-sliders-h mr-1",
                            href="/parametres",
                            id="params",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Paramètres chantier", target="params", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-cloud-upload-alt mr-1",
                            href="/export",
                            id="export",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Importer un fichier", target="export", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            id="pdf",
                            href="/rapport",
                            className="fas fa-file-pdf mr-1",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Exporter en PDF", target="pdf", placement="down"),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-user-circle mr-1",
                            href="/profil",
                            id="profil",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip(
                            "Modifier le profil", target="profil", placement="down"
                        ),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-question-circle mr-1",
                            href="/aide",
                            id="aide",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Aide", target="aide", placement="down"),
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Button(
                            className="fas fa-sign-out-alt mr-1",
                            href="/logout",
                            id="logout",
                            style={"height": "30px", "width": "50px"},
                        ),
                        dbc.Tooltip("Déconnexion", target="logout", placement="down"),
                    ]
                ),
            ],
            no_gutters=True,
            className="ml-auto flex-nowrap mt-3 mt-md-0",
            align="center",
        )
    return buttons


###     CREATION DE LA BARRE DE NAVIGATION
def return_navbar(profil):
    navbar = dbc.Navbar(
        [
            html.A(
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app.get_asset_url("logo.png"), height="55px")
                        ),
                    ],
                    align="center",
                    no_gutters=True,
                ),
                href="https://fr.enneade-ingenierie.com",
            ),
            html.H4(id="title_chantier"),
            return_buttons(profil),
        ],
        color="dark",
        dark=True,
        style=dict(height=60),
    )
    return navbar

###     AFFICHAGE DU CHANTIER SELECTIONNE SUR LA BARRE DE NAVIGATION
@app.callback(Output("title_chantier", "children"), Input("chantier-select", "data"))
def afficher_nom_chantier(chantier):
    if chantier == {}:
        return "Aucun chantier sélectionné"
    else:
        return f"{chantier}"


# @app.callback(Output("page-content", "children"), Input("url", "pathname"))
# def display_page(pathname):
#     if pathname == "/":
#         return home.layout
#     if pathname == "/login":
#         return login.layout
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
#     elif pathname == "/rapport":
#         return synthese.layout
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


###     AFFICHE LA PAGE DEMANDE EN FONCTION DE L'URL, ETAT DE CONNEXION ET PROFIL UTILISATEUR
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
    elif pathname == "/rapport":
        if current_user.is_authenticated:
            return synthese.layout
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


####     AFFICHAGE DE LA BARRE DE NAVIGATION APRES LOGIN
@app.callback(
    Output("navBar", "children"),
    [Input("page-content", "children"), Input("url", "pathname")],
)
def navBar(input1, url):
    if url == "/" or url == "/creation" or url == "/logout" or url == "/login_fd":
        return []
    else:
        if current_user.is_authenticated:
        # if True:
            return return_navbar(user_profil)
        else:
            return []


#### EXECUTE LES SERVEUR LORSQUE LE FICHIER APP.PY EST APPELE
if __name__ == "__main__":
    app.run_server(debug=True)
