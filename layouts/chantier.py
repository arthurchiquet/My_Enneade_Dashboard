import dash_core_components as dcc
import dash_html_components as html
import dash_gif_component as gif
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import dash_table as dt
import warnings
from server import app
from config import engine
from data import get_data, save_json, download_json, memoized_data
from utils_maps import update_map_chantier, empty_figure, extract_position
import utils_topo, utils_inclino, utils_jauge, utils_tirant, utils_piezo
import json

warnings.filterwarnings("ignore")

colors = {"background": "#222222", "text": "#FF8C00"}

layout = html.Div(
    children=[
        html.Br(),
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
    [
        Input("chantier-select", "data"),
        Input("global-params", "data"),
    ],
)
def affichage_map(chantier, params):
    try:
        return update_map_chantier(chantier, params), ''
    except:
        return empty_figure(), 'Aucune donnée à afficher'


@app.callback(
    Output("global-params", "data"),
    Input("provis-params", "data"),
    Input("chantier-select", "data"),
)
def update_params(params, chantier):
    if chantier == {}:
        return {}
    else:
        if params == {}:
            try:
                params = download_json(chantier, "paramètres", "positions.json")
            except:
                params = {}
            try:
                data = memoized_data(chantier, "actif", "topographie", "topo.csv")
                data_positions = extract_position(data)
                capteurs = {"cible": data_positions.to_dict("index")}
                params.update(capteurs)
            except:
                param={}
        else:
            pass
        return params

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
        State("global-params", "data"),
    ],
)
def display_right_content(options, clickData, params):
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
        if "secteur" in params.keys():
            options_secteur = [{"label": secteur, "value": secteur} for secteur in params["secteur"]]
        else:
            options_secteur=[]
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
    State("global-params", "data"),)
def return_input_dropdown(option, param, params):
    if option==1:
        return {'display':'inline'}, {'display':'none'},[]
    elif option == 2 or option ==3:
        if param==1:
            if 'secteur' in params.keys():
                options=[{"label": secteur, "value": secteur} for secteur in params["secteur"]]
            else:
                options=[]
        elif param ==3:
            if 'inclino' in params.keys():
                options=[{"label": inclino, "value": inclino} for inclino in params["inclino"]]
            else:
                options=[]
        elif param ==4:
            if 'tirant' in params.keys():
                options=[{"label": tirant, "value": tirant} for tirant in params["tirant"]]
            else:
                options=[]
        elif param ==5:
            if 'jauge' in params.keys():
                options=[{"label": jauge, "value": jauge} for jauge in params["jauge"]]
            else:
                options=[]
        elif param ==6:
            if 'piezo' in params.keys():
                options=[{"label": piezo, "value": piezo} for piezo in params["piezo"]]
            else:
                options=[]
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
        State("global-params", "data"),
    ],
)
def select_secteur(n_clicks, secteur_selected, params):
    if n_clicks > 0:
        secteurs_params = params["secteur"]
        secteur = secteurs_params[secteur_selected]
        del params["secteur"]
        df = (
            pd.concat(
                {k: pd.DataFrame.from_dict(v, "index") for k, v in params.items()},
                axis=0,
            )
            .reset_index()
            .rename(columns={"level_0": "type", "level_1": "capteur"})
        )
        capteurs = df[
            (df.lon > secteur[0][0])
            & (df.lon < secteur[1][0])
            & (df.lat < secteur[0][1])
            & (df.lat > secteur[1][1])
        ]
        return {
            secteur_selected: {
                t: capteurs[capteurs["type"] == t]["capteur"].tolist()
                for t in capteurs["type"].unique()
            }
        }
    else:
        return {}


@app.callback(
    Output("update-success", "children"),
    Output("provis-params", "data"),
    [
        Input("save-update", "n_clicks"),
        State("type_option", "value"),
        State("type_param", "value"),
        State("nom_param_1", "value"),
        State("nom_param_2", "value"),
        State("map-chantier", "selectedData"),
        State("global-params", "data"),
        State("chantier-select", "data"),
    ],
)
def add_modif_param(n_clicks, option, param, nom_param1, nom_param2, selectedData, params, chantier):
    if option ==1:
        nom_param = nom_param1
    elif option == 2 or option == 3:
        nom_param = nom_param2
    if option == 1 or option == 2:
        if selectedData:
            range_selection = selectedData["range"]["mapbox"]
            lat = (range_selection[0][1] + range_selection[1][1]) / 2
            lon = (range_selection[0][0] + range_selection[1][0]) / 2
            if param == 1:
                try:
                    params["secteur"][nom_param] = range_selection
                except:
                    params["secteur"] = {nom_param: range_selection}
                save_json(params, chantier, "paramètres", "positions.json"), params
                return "Les paramètres ont bien été enregistrés", params
            elif param == 2:
                return "", params
            elif param == 3:
                try:
                    params["inclino"][nom_param] = {"lat": lat, "lon": lon}
                except:
                    params["inclino"] = {nom_param: {"lat": lat, "lon": lon}}
                save_json(params, chantier, "paramètres", "positions.json")
                return "Les paramètres ont bien été enregistrés", params
            elif param == 4:
                try:
                    params["tirant"][nom_param] = {"lat": lat, "lon": lon}
                except:
                    params["tirant"] = {nom_param: {"lat": lat, "lon": lon}}
                save_json(params, chantier, "paramètres", "positions.json")
                return "Les paramètres ont bien été enregistrés", params
            elif param == 5:
                try:
                    params["jauge"][nom_param] = {"lat": lat, "lon": lon}
                except:
                    params["jauge"] = {nom_param: {"lat": lat, "lon": lon}}
                save_json(params, chantier, "paramètres", "positions.json")
                return "Les paramètres ont bien été enregistrés", params
            elif param == 6:
                try:
                    params["piezo"][nom_param] = {"lat": lat, "lon": lon}
                except:
                    params["piezo"] = {nom_param: {"lat": lat, "lon": lon}}
                save_json(params, chantier, "paramètres", "positions.json")
                return "Les paramètres ont bien été enregistrés", params
            else:
                return "", params

    elif option == 3:
        if param == 1:
            del params["secteur"][nom_param]
            save_json(params, chantier, "paramètres", "positions.json")
            return "Le secteur a bien été supprimé", params
        elif param == 2:
            return "", params
        elif param == 3:
            del params["inclino"][nom_param]
            save_json(params, chantier, "paramètres", "positions.json")
            return "L'inclinomètre a bien été supprimé", params
        elif param == 4:
            del params["tirant"][nom_param]
            save_json(params, chantier, "paramètres", "positions.json")
            return "Le tirant a bien été supprimé", params
        elif param == 5:
            del params["jauge"][nom_param]
            save_json(params, chantier, "paramètres", "positions.json")
            return "La jauge a bien été supprimé", params
        elif param == 6:
            del params["piezo"][nom_param]
            save_json(params, chantier, "paramètres", "positions.json")
            return "Le piezomètre a bien été supprimé", params
        else:
            return "", params
    else:
        return "", params


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
            sous_titre(customdata),
        )
    except:
        return "", empty_figure(), f"Aucune donnée existante pour cet élément"


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
