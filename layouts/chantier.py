import dash_core_components as dcc
import dash_html_components as html
import dash_gif_component as gif
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
from google.cloud.exceptions import NotFound
import plotly.graph_objects as go
import pandas as pd
import dash_table as dt
import warnings
from server import app
from config import engine
from pangres import upsert
from data import memoized_data
from utils_maps import update_map_chantier, empty_figure, extract_position
from params_mgmt import ajout_secteur, ajout_capteur, maj_secteur, maj_capteur, supp_secteur, supp_capteur
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo

warnings.filterwarnings("ignore")

colors = {"background": "#222222", "text": "#FF8C00"}

layout = html.Div(
    children=[
        html.Br(),
        html.Div(id='reload-map'),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            dbc.Container(id='map-container',
                                children=[
                                    dbc.Row(html.H4(id='no-chantier-selected', children='Chargement des données en cours ...'), justify='center'),
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
                                                    dbc.Tab(labelClassName="fas fa-hand-pointer", tab_id='control-map'),
                                                    dbc.Tab(labelClassName="fas fa-sliders-h", tab_id='modify-map'),
                                                    dbc.Tab(labelClassName="far fa-object-ungroup", tab_id='select-map'),

                                                ],
                                                id= 'options-map',
                                                active_tab="control-map",
                                            )
                                        ],
                                        justify="center",
                                    ),
                                ], fluid=True
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


### AFFICHAGE LA CARTE DU CHANTIER SELECTIONNE #####
@app.callback(
    Output("map-chantier", "figure"),
    Output("no-chantier-selected", "children"),
    Input('reload-map', 'children'),
    Input("chantier-select", "data"),
)
def affichage_map(reload, chantier):
    try:
        return update_map_chantier(chantier), ''
    except ValueError:
        return empty_figure(), 'Aucune donnée à afficher'

collapse = html.Div(
    [
        html.Br(),
        dbc.Row(dbc.Button(id="help", className="fas fa-info-circle"), justify="center"),
        dbc.Collapse(
            dbc.Card(dbc.CardBody([dbc.Row(gif.GifPlayer(gif='assets/help.gif', still='statique.png'), justify='center')])),
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
    if n:
        return not is_open
    return is_open


@app.callback(
    Output("right-content", "children"),
    [
        Input("options-map", "active_tab"),
        Input("map-chantier", "clickData"),
    ],
        State('chantier-select', 'data')
)
def display_right_content(options, clickData, chantier):
    if options=='control-map':
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
    elif options=='modify-map':
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
                            dbc.Input(placeholder="Nom du paramètre", id="nom_param_1", style={'display':'none'}),
                            dcc.Dropdown(
                                id="nom_param_2",
                                style={'display':'none'},
                            ),
                            html.Br(),
                            html.Br(),
                            dbc.Row(
                                dbc.Button(
                                    id="save-update",
                                    href="/chantier",
                                    n_clicks=0,
                                    className='fas fa-save',
                                    size='lg',
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
            )
        ]
    elif options=='select-map':
        with engine.connect() as con:
            query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}'"
            liste_secteurs=pd.read_sql_query(query3, con=con).nom_secteur.tolist()
        options_secteur = [{"label": secteur, "value": secteur} for secteur in liste_secteurs]
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
                                    style={"color": "black", 'width': '150px'},
                                    options=options_secteur
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
                                    size='lg'
                                ),
                                justify="center",
                            ),
                        ]
                    ),
                ],
                style={"width": "41rem"},
            )
        ]


@app.callback(
    Output('nom_param_1', 'style'),
    Output('nom_param_2', 'style'),
    Output('nom_param_2', 'options'),
    Input('type_option', 'value'),
    Input('type_param', 'value'),
    State('chantier-select', 'data')
)
def return_input_dropdown(option, param, chantier):
    if option==1:
        return {'display':'inline'}, {'display':'none'},[]
    elif option == 2 or option ==3:
        with engine.connect() as con:
            query2 = f"SELECT * FROM capteur where nom_chantier = '{chantier}'"
            query3 = f"SELECT * FROM secteur where nom_chantier = '{chantier}'"
            liste_capteurs=pd.read_sql_query(query2, con=con)
            liste_secteurs=pd.read_sql_query(query3, con=con).nom_secteur.tolist()
        liste_inclino = liste_capteurs[liste_capteurs.type=='inclino'].nom_capteur.tolist()
        liste_tirant = liste_capteurs[liste_capteurs.type=='tirant'].nom_capteur.tolist()
        liste_jauge = liste_capteurs[liste_capteurs.type=='jauge'].nom_capteur.tolist()
        liste_piezo = liste_capteurs[liste_capteurs.type=='piezo'].nom_capteur.tolist()
        if param==1:
            options=[{"label": secteur, "value": secteur} for secteur in liste_secteurs]
        elif param ==3:
            options=[{"label": inclino, "value": inclino} for inclino in liste_inclino]
        elif param ==4:
            options=[{"label": tirant, "value": tirant} for tirant in liste_tirant]
        elif param ==5:
            options=[{"label": jauge, "value": jauge} for jauge in liste_jauge]
        elif param ==6:
            options=[{"label": piezo, "value": piezo} for piezo in liste_piezo]
        else:
            options=[]

        return {'display':'none'}, {"color": "black","width": "100%"}, options
    else:
        return {'display':'none'}, {'display':'none'},[]


@app.callback(
    Output("secteur-select", "data"),
    [
        Input("go-secteur", "n_clicks"),
        State("secteur-selection", "value"),
        State('chantier-select', 'data')
    ],
)
def select_secteur(n_clicks, secteur_selected, chantier):
    if n_clicks > 0:
        # try:
        #     df = extract_position(memoized_data(chantier, "actif", "topographie", "topo.csv"))
        #     with engine.connect() as con:
        #         query2 = f"SELECT * FROM capteur where chantier = '{chantier}'"
        #         query3 = f"SELECT * FROM secteur where chantier = '{chantier}' and secteur='{secteur_selected}'"
        #         liste_capteurs=pd.read_sql_query(query2, con=con)
        #         liste_secteurs=pd.read_sql_query(query3, con=con)
        #     lat1=liste_secteurs.lat1[0]
        #     lat2=liste_secteurs.lat2[0]
        #     lon1=liste_secteurs.lon1[0]
        #     lon2=liste_secteurs.lon2[0]

        #     cibles_select =
        #     capteurs = liste_capteurs[
        #         (liste_capteurs.lon > lon1)
        #         & (liste_capteurs.lon < lon2)
        #         & (liste_capteurs.lat > lat1)
        #         & (liste_capteurs.lat < lat2)
        #     ]
        # except IndexError:
        #     return {}


        return secteur_selected
    else:
        return {}


@app.callback(
    Output("update-success", "children"),
    Output('reload-map', 'children'),
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
def add_modif_param(n_clicks, option, param, nom_param1, nom_param2, selectedData, chantier):
    if option == 1:
        if selectedData:
            nom_param = nom_param1
            range_selection = selectedData["range"]["mapbox"]
            lat = (range_selection[0][1] + range_selection[1][1]) / 2
            lon = (range_selection[0][0] + range_selection[1][0]) / 2
            if param == 1:
                lon1=range_selection[0][0]
                lon2=range_selection[1][0]
                lat1=range_selection[0][1]
                lat2=range_selection[1][1]
                if n_clicks:
                    ajout_secteur(nom_param, chantier, lat1, lat2, lon1, lon2)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 2:
                return "", ''
            elif param == 3:
                if n_clicks:
                    ajout_capteur(nom_param, chantier, 'inclino', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 4:
                if n_clicks:
                    ajout_capteur(nom_param, chantier, 'tirant', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 5:
                if n_clicks:
                    ajout_capteur(nom_param, chantier, 'jauge', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 6:
                if n_clicks:
                    ajout_capteur(nom_param, chantier, 'piezo', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            else:
                return "", ''
    elif option == 2:
        if selectedData:
            nom_param = nom_param2
            range_selection = selectedData["range"]["mapbox"]
            lat = (range_selection[0][1] + range_selection[1][1]) / 2
            lon = (range_selection[0][0] + range_selection[1][0]) / 2
            if param == 1:
                lon1=range_selection[0][0]
                lon2=range_selection[1][0]
                lat1=range_selection[0][1]
                lat2=range_selection[1][1]
                if n_clicks:
                    maj_secteur(nom_param, chantier, lat1, lat2, lon1, lon2)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 2:
                return "", ''
            elif param == 3:
                if n_clicks:
                    maj_capteur(nom_param, chantier, 'inclino', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 4:
                if n_clicks:
                    maj_capteur(nom_param, chantier, 'tirant', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 5:
                if n_clicks:
                    maj_capteur(nom_param, chantier, 'jauge', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            elif param == 6:
                if n_clicks:
                    maj_capteur(nom_param, chantier, 'piezo', lat, lon)
                    return "Les paramètres ont bien été enregistrés", ''
            else:
                return "", ''

    elif option == 3:
        nom_param = nom_param2
        if param == 1:
            if n_clicks:
                supp_secteur(nom_param, chantier)
                return "Le secteur a bien été supprimé", ''
        elif param == 2:
            return "", ''
        elif param == 3:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "L'inclinomètre a bien été supprimé", ''
        elif param == 4:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "Le tirant a bien été supprimé", ''
        elif param == 5:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "La jauge a bien été supprimé", ''
        elif param == 6:
            if n_clicks:
                supp_capteur(nom_param, chantier)
                return "Le piezomètre a bien été supprimé", ''
        else:
            return "", ''
    else:
        return '', ''


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
        customdata = selectedData["points"][0]["customdata"][0]
        text = selectedData["points"][0]["text"]
        return (
            text,
            selection_affichage(chantier, customdata, text),
            sous_titre(customdata)
            )
    except :
        return "", empty_figure(), "Aucune donnée existante pour cet élément"


### RENVOIE LA METHODE D'AFFICHAGE DE LA COURBE EN FONCTION DU TYPE DE CAPTEUR ####
def selection_affichage(chantier, customdata, text):
    if customdata == "cible":
        df = memoized_data(chantier, "actif", "topographie", "topo.csv")
        df = utils_topo.format_df(df, text, angle=0, repere='xyz')
        return utils_topo.graph_topo(
            df, height=550, spacing=0.06, showlegend=False
        )
    elif customdata == "inclino":
        return utils_inclino.graph_inclino(chantier, text, height=550)
    elif customdata == "tirant":
        return utils_tirant.graph_tirant(chantier, text, height=550, mode=2)
    elif customdata == "jauge":
        return utils_jauge.graph_jauge(chantier, text, height=550)
    elif customdata == "piezo":
        return utils_piezo.graph_piezo(chantier, text)
    else:
        return empty_figure()


def sous_titre(customdata):
    if customdata == "cible":
        return "Déplacements 3 axes (mm)"
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
