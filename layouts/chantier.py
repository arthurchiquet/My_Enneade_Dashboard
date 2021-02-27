#### Import des modules dash

import dash_core_components as dcc
import dash_html_components as html
import dash_gif_component as gif
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash_table as dt

#### Import des librairies
import plotly.graph_objects as go
import pandas as pd
from pangres import upsert
import warnings


from server import app
from config import engine
from data import memoized_data, list_files
from utils_maps import update_map_chantier, empty_figure, extract_position
from params_mgmt import (
    ajout_secteur,
    ajout_capteur,
    maj_secteur,
    maj_capteur,
    supp_secteur,
    supp_capteur,
)
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

warnings.filterwarnings("ignore")

colors = {"background": "#222222", "text": "#FF8C00"}


#### Definition de l'interface (page chantier)

layout = html.Div(
    children=[
        html.Br(),
        html.Div(id="reload-map"),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(
                                id="map-container",
                                children=[
                                    dbc.Row(
                                        html.H4(
                                            id="no-chantier-selected",
                                            children="Chargement des données en cours ...",
                                        ),
                                        justify="center",
                                    ),
                                    dcc.Graph(
                                        id="map-chantier",
                                        config={
                                            "scrollZoom": True,
                                            "modeBarButtonsToRemove": ["lasso2d"],
                                        },
                                        figure=empty_figure(),
                                    ),
                                    html.Br(),
                                    dbc.Row(
                                        [
                                            dbc.Tabs(
                                                [
                                                    dbc.Tab(
                                                        labelClassName="fas fa-hand-pointer",
                                                        tab_id="control-map",
                                                    ),
                                                    dbc.Tab(
                                                        labelClassName="fas fa-sliders-h",
                                                        tab_id="modify-map",
                                                    ),
                                                    dbc.Tab(
                                                        labelClassName="far fa-object-ungroup",
                                                        tab_id="select-map",
                                                    ),
                                                ],
                                                id="options-map",
                                                active_tab="control-map",
                                            )
                                        ],
                                        justify="center",
                                    ),
                                ],
                                fluid=True,
                            ),
                            justify="center",
                        )
                    ]
                ),
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(
                                id="right-content",
                                children=[],
                            ),
                            justify="center",
                        ),
                    ]
                ),
            ]
        ),
    ]
)


### AFFICHE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    Output("no-chantier-selected", "children"),
    Input("chantier-select", "data"),
    Input("reload-map", "children"),
)
def affichage_map(chantier, reload):

    ''' Voir utils_maps pour plus d'information
    sur la fonction update_map_chantier '''

    try:
        return update_map_chantier(chantier), ""
    except:
        return empty_figure(), "Aucune donnée à afficher"

#### Création d'une zone depliable associé au bouton 'Aide'
collapse = html.Div(
    [
        html.Br(),
        dbc.Row(
            dbc.Button(id="help", className="fas fa-info-circle"), justify="center"
        ),
        dbc.Collapse(
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Row(
                            gif.GifPlayer(gif="assets/help.gif", still="statique.png"),
                            justify="center",
                        )
                    ]
                )
            ),
            id="card-help",
        ),
    ]
)


@app.callback(
    Output("card-help", "is_open"),
    [Input("help", "n_clicks")],
    [State("card-help", "is_open")],
)
def collapse_parametres(n, is_open):
    ''' Ouvre ou ferme la zone ci-dessus
        lors du clique sur le bouton (Aide)'''

    if n:
        return not is_open
    return is_open


#### Affiche le contenu situé a droite de la CARTE
#### en fonction de l'option selectionnée

@app.callback(
    Output("right-content", "children"),
    [
        Input("options-map", "active_tab"),
        Input("map-chantier", "clickData"),
    ],
    State("chantier-select", "data"),
)
def display_right_content(options, clickData, chantier):

    '''
    Option 1 : Manipulation -> Affiche la courbe CORRESPONDANT
    au capteur selectionné directement sur la carte

    Option 2 : Modification -> Affiche une fenètre de modification des paramètre
    avec zone de saisie et enregistrement des modifs

    Option 3: Selection -> Affiche un menu déroulant permettant de
    sélectionné un secteur pré-défini et un bouton renvoyant à la page
    de synthèse par secteur
    '''


    if options == "control-map":
        if clickData:
            return [
                dbc.Row(html.H3(id="titre_graph"), justify="center"),
                dbc.Row(dbc.Label(id="sous_titre_graph"), justify="center"),
                dcc.Loading(
                    id="loading-graph",
                    color="#FF8C00",
                    type="graph",
                    children=dcc.Graph(id="courbe_capteur", figure=empty_figure()),
                ),
            ]
        else:
            return []

    elif options == "modify-map":
        return [
            html.Br(),
            html.Br(),
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(html.H4("Ajouter ou modifier"), justify="center")
                    ),
                    collapse,
                    dbc.CardBody(
                        [
                            dcc.Dropdown(
                                id="type_option",
                                style={"color": "black"},
                                options=[
                                    {"label": "Ajouter", "value": 1},
                                    {"label": "Modifier", "value": 2},
                                    {"label": "Supprimer", "value": 3},
                                ],
                                placeholder="Options",
                                clearable=False,
                            ),
                            html.Br(),
                            dcc.Dropdown(
                                id="type_param",
                                style={"color": "black"},
                                options=[
                                    {"label": "Secteur", "value": 1},
                                    {"label": "Inclinomètre", "value": 3},
                                    {"label": "Tirant", "value": 4},
                                    {"label": "Jauge", "value": 5},
                                    {"label": "Piezomètre", "value": 6},
                                ],
                                placeholder="Choix du paramètre",
                                clearable=False,
                            ),
                            html.Br(),
                            dbc.Input(
                                placeholder="Nom du paramètre",
                                id="nom_param_1",
                                style={"display": "none"},
                            ),
                            dcc.Dropdown(
                                id="nom_param_2",
                                style={"display": "none"},
                            ),
                            html.Br(),
                            html.Br(),
                            dbc.Row(
                                dbc.Button(
                                    id="save-update",
                                    href="/chantier",
                                    n_clicks=0,
                                    className="fas fa-save",
                                    size="lg",
                                ),
                                justify="center",
                            ),
                            html.Br(),
                            dbc.Row(
                                html.Div(id="update-success", className="text-success"),
                                justify="center",
                            ),
                        ]
                    ),
                ],
                style={"width": "41rem"},
            ),
        ]

    elif options == "select-map":
        with engine.connect() as con:
            query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}'"
            liste_secteurs = pd.read_sql_query(query3, con=con).nom_secteur.tolist()
        options_secteur = [
            {"label": secteur, "value": secteur} for secteur in liste_secteurs
        ]
        return [
            html.Br(),
            html.Br(),
            dbc.Card(
                [
                    dbc.CardHeader(
                        dbc.Row(html.H4("Sélectionner un secteur"), justify="center")
                    ),
                    dbc.CardBody(
                        [
                            dbc.Row(dbc.Label("Choix du secteur"), justify="center"),
                            dbc.Row(
                                dcc.Dropdown(
                                    id="secteur-selection",
                                    style={"color": "black", "width": "150px"},
                                    options=options_secteur,
                                ),
                                justify="center",
                            ),
                            html.Br(),
                            dbc.Row(
                                dbc.Button(
                                    id="go-secteur",
                                    href="/secteur",
                                    n_clicks=0,
                                    className="fas fa-chart-line",
                                    size="lg",
                                ),
                                justify="center",
                            ),
                        ]
                    ),
                ],
                style={"width": "41rem"},
            ),
        ]


#### Permet de pré-définir les valeurs des menus déroulant
#### définis ci-dessus
@app.callback(
    Output("nom_param_1", "style"),
    Output("nom_param_2", "style"),
    Output("nom_param_2", "options"),
    Input("type_option", "value"),
    Input("type_param", "value"),
    State("chantier-select", "data"),
)
def return_input_dropdown(option, param, chantier):
    '''

    si l'option (ajouter) est sélectionné et le type de paramètre
    est (secteur) on affiche une
    zone de saisie du paramètre manuelle et non un menu déroulant

    si l'option (ajouter) est sélectionnée on affiche un menu déroulant renvoyant
    la liste des paramètres dont les données existent déja notre BDD

    si l'une des options (modifier ou supprimer) est sélectionnée on affiche un menu déroulant renvoyant
    la liste des paramètres ayant déjà été préalablement ajoutés
    '''

    if option == 1 and param == 1:
        return {"display": "inline"}, {"display": "none"}, []

    elif option == 1:
        if param == 3:
            liste = list_files(f"{chantier}/actif/inclinometrie/")
            options = [{"label": inclino, "value": inclino} for inclino in liste]
        elif param == 4:
            liste = list_files(f"{chantier}/actif/tirant/")
            options = [{"label": tirant, "value": tirant} for tirant in liste]
        elif param == 5:
            liste = list_files(f"{chantier}/actif/jauge/")
            options = [{"label": jauge, "value": jauge} for jauge in liste]
        elif param == 6:
            liste = list_files(f"{chantier}/actif/piezometrie/")
            options = [{"label": piezo, "value": piezo} for piezo in liste]
        else:
            options = []
        return {"display": "none"}, {"color": "black", "width": "100%"}, options

    elif option == 2 or option == 3:
        with engine.connect() as con:
            query2 = f"SELECT * FROM capteur where nom_chantier = '{chantier}'"
            query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}'"
            liste_capteurs = pd.read_sql_query(query2, con=con)
            liste_secteurs = pd.read_sql_query(query3, con=con).nom_secteur.tolist()
        liste_inclino = liste_capteurs[liste_capteurs.type == "inclino"].nom_capteur.tolist()
        liste_tirant = liste_capteurs[liste_capteurs.type == "tirant"].nom_capteur.tolist()
        liste_jauge = liste_capteurs[liste_capteurs.type == "jauge"].nom_capteur.tolist()
        liste_piezo = liste_capteurs[liste_capteurs.type == "piezo"].nom_capteur.tolist()
        if param == 1:

            ''' param 1 = secteur'''
            options = [{"label": secteur, "value": secteur} for secteur in liste_secteurs]

        elif param == 3:

            ''' param 3 = Inclinomètre'''
            options = [{"label": inclino, "value": inclino} for inclino in liste_inclino]

        elif param == 4:

            ''' param 1 = Tirant'''
            options = [{"label": tirant, "value": tirant} for tirant in liste_tirant]

        elif param == 5:

            ''' param 1 = Jauge'''
            options = [{"label": jauge, "value": jauge} for jauge in liste_jauge]

        elif param == 6:

            ''' param 1 = Piezomètre'''
            options = [{"label": piezo, "value": piezo} for piezo in liste_piezo]

        else:
            options = []

        return {"display": "none"}, {"color": "black", "width": "100%"}, options

    else:
        return {"display": "none"}, {"display": "none"}, []


#### Modication et sauvegarde des paramètres
@app.callback(
    Output("update-success", "children"),
    Output("reload-map", "children"),
    [
        Input("save-update", "n_clicks"),
        State("type_option", "value"),
        State("type_param", "value"),
        State("nom_param_1", "value"),
        State("nom_param_2", "value"),
        State("map-chantier", "selectedData"),
        State("chantier-select", "data"),
    ],
)
def add_modif_param(
    n_clicks, option, param, nom_param1, nom_param2, selectedData, chantier
):
    '''
    Option 1 : Ajouter
    Option 2 : Modifier
    Option 3 : Supprimer


    '''

    if option == 1:

        ''' SelectedData : dictionnaire retourner par plotly lors
        d'une sélection sur la zone graphique'''

        ''' plus d'infos sur les fonctions ajout_capteur,
        ajout_secteur, ajout_capteur, maj_secteur, maj_capteur, supp_secteur,supp_capteur
        dans (params_mgmt)'''

        if selectedData:

            #range_selection : liste de liste de coordonnées GPS
            #correspondant à la zone sélectionnée

            range_selection = selectedData["range"]["mapbox"]

            #définition de la latitude et longitude pour le positionnement des capteurs

            lat = (range_selection[0][1] + range_selection[1][1]) / 2
            lon = (range_selection[0][0] + range_selection[1][0]) / 2

            if param == 1:

                #paramètre : Secteur

                nom_param = nom_param1
                lat2 = range_selection[0][1]
                lat1 = range_selection[1][1]
                lon2 = range_selection[1][0]
                lon1 = range_selection[0][0]
                if n_clicks:
                    ajout_secteur(nom_param, chantier, lat1, lat2, lon1, lon2)
                    return "Les paramètres ont bien été enregistrés", ""

            elif param == 2:
                return "", ""
            elif param == 3:

                #paramètre : Inclinomètre

                nom_param = nom_param2
                if n_clicks:
                    ajout_capteur(nom_param, chantier, "inclino", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""

            elif param == 4:

                #paramètre : Tirant

                nom_param = nom_param2
                if n_clicks:
                    ajout_capteur(nom_param, chantier, "tirant", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""

            elif param == 5:

                #paramètre : Jauge

                nom_param = nom_param2
                if n_clicks:
                    ajout_capteur(nom_param, chantier, "jauge", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""

            elif param == 6:

                #paramètre : Piezomètre

                nom_param = nom_param2
                if n_clicks:
                    ajout_capteur(nom_param, chantier, "piezo", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""
            else:
                return "", ""

    elif option == 2:
        if selectedData:
            nom_param = nom_param2
            range_selection = selectedData["range"]["mapbox"]
            lat = (range_selection[0][1] + range_selection[1][1]) / 2
            lon = (range_selection[0][0] + range_selection[1][0]) / 2
            if param == 1:
                lat2 = range_selection[0][1]
                lat1 = range_selection[1][1]
                lon2 = range_selection[1][0]
                lon1 = range_selection[0][0]
                if n_clicks:
                    maj_secteur(nom_param, chantier, lat1, lat2, lon1, lon2)
                    return "Les paramètres ont bien été enregistrés", ""
            elif param == 2:
                return "", ""
            elif param == 3:
                if n_clicks:
                    maj_capteur(nom_param, chantier, "inclino", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""
            elif param == 4:
                if n_clicks:
                    maj_capteur(nom_param, chantier, "tirant", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""
            elif param == 5:
                if n_clicks:
                    maj_capteur(nom_param, chantier, "jauge", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""
            elif param == 6:
                if n_clicks:
                    maj_capteur(nom_param, chantier, "piezo", lat, lon)
                    return "Les paramètres ont bien été enregistrés", ""
            else:
                return "", ""

    elif option == 3:
        nom_param = nom_param2
        if param == 1:
            if n_clicks:
                supp_secteur(nom_param, chantier)
                return "Le secteur a bien été supprimé", ""
        elif param == 2:
            return "", ""
        elif param == 3:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "L'inclinomètre a bien été supprimé", ""
        elif param == 4:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "Le tirant a bien été supprimé", ""
        elif param == 5:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "La jauge a bien été supprimé", ""
        elif param == 6:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "Le piezomètre a bien été supprimé", ""
        else:
            return "", ""
    else:
        return "", ""


#### Stocke la valeur du secteur sélectionné et l'ensemble
#### des capteurs se situant à l'intérieur de celui-ci
@app.callback(
    Output("secteur-select", "data"),
    [
        Input("go-secteur", "n_clicks"),
        State("secteur-selection", "value"),
        State("chantier-select", "data"),
    ],
)
def select_secteur(n_clicks, secteur_selected, chantier):
    if n_clicks > 0:
        try:

            ''' extract_position retourne les positions GPS initiales des cibles topo
            issues du fichier de déplacement des cibles'''

            df = extract_position(
                memoized_data(chantier, "actif", "topographie", "topo.csv")
            )

            ''' récupération des coordonées GPS du secteur sélectionné ainsi que les
            coordonnées de l'ensemble des autres capteurs '''
            with engine.connect() as con:
                query2 = f"SELECT * FROM capteur where nom_chantier = '{chantier}'"
                query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}' and nom_secteur='{secteur_selected}'"
                liste_capteurs = pd.read_sql_query(query2, con=con)
                liste_secteurs = pd.read_sql_query(query3, con=con)
            lat1 = liste_secteurs.lat1[0]
            lat2 = liste_secteurs.lat2[0]
            lon1 = liste_secteurs.lon1[0]
            lon2 = liste_secteurs.lon2[0]

            ''' filtre l'ensmble des cibles dont la latitude et longitude est comprise
            dans la zone correspondant au secteur et retourne le resultat sous forme
            d'un dictionnaire'''
            cibles_select = df[
                (df.lat > lat1) & (df.lat < lat2) & (df.lon > lon1) & (df.lon < lon2)
            ]
            cibles_select = {"cible": cibles_select.cible.tolist()}

            ''' idem pour les autres capteurs'''
            capteurs_select = liste_capteurs[
                (liste_capteurs.lon > lon1)
                & (liste_capteurs.lon < lon2)
                & (liste_capteurs.lat < lat1)
                & (liste_capteurs.lat > lat2)
            ]
            capteurs_select = {
                type: capteurs_select[capteurs_select.type == type].nom_capteur.tolist()
                for type in capteurs_select.type
            }

            ''' création d'un dictionnaire associant à chaque type de
            paramètre ses coordonnées correspondantes'''

            selection = {"secteur": secteur_selected}
            selection.update(cibles_select)
            selection.update(capteurs_select)
            return selection
        except IndexError:
            return {}
    else:
        return {}


### AFFICHE LA COURBE CORRESPONDANT AU CAPTEUR SELECTIONNÉ ####
@app.callback(
    [
        Output("titre_graph", "children"),
        Output("courbe_capteur", "figure"),
        Output("sous_titre_graph", "children"),
    ],
    [Input("map-chantier", "selectedData"), State("chantier-select", "data")],
)
def affichage_courbe_capteur(selectedData, chantier):
    try:
        ''' SelectedData : dictionnaire retourner par plotly lors
        d'une sélection sur la zone graphique'''

        '''En fonction du type de capteur sélectionné sur la carte
        la méthode appelle des focntions spécifiques pour récuper les données
        les mettre en forme et tracer les courbes'''

        customdata = selectedData["points"][0]["customdata"]
        text = selectedData["points"][0]["text"]
        if customdata == "cible":
            df = memoized_data(chantier, "actif", "topographie", "topo.csv")
            df = utils_topo.format_df(df, text, angle=0, repere="xyz")
            fig = utils_topo.graph_topo(df, height=550, spacing=0.06, showlegend=False)
        elif customdata == "inclino":
            fig = utils_inclino.graph_inclino(chantier, text, height=550)
        elif customdata == "tirant":
            fig = utils_tirant.graph_tirant(chantier, text, height=550, mode=2)
        elif customdata == "jauge":
            fig = utils_jauge.graph_jauge(chantier, text, height=550)
        elif customdata == "piezo":
            fig = utils_piezo.graph_piezo(chantier, text)
        else:
            fig = empty_figure()
        return (text, fig, sous_titre(customdata))
    except:
        return "", empty_figure(), "Aucune donnée existante pour cet élément"


def sous_titre(customdata):
    if customdata == "cible":
        return "Déplacements X, Y, Z (mm)"
    elif customdata == "inclino":
        return ""
    elif customdata == "tirant":
        return "Evolution de la charge (%tb)"
    elif customdata == "jauge":
        return "Evolution brute des fissures (Ecarts, mm)"
    elif customdata == "piezo":
        return ""
    else:
        return ""
