#### Import des modules dash

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table as dt

#### Import des librairies python
import pandas as pd
import warnings
from pangres import upsert

from data import get_data, export_data
from server import app
from config import engine
from data import memoized_data
from chantier_mgmt import update_chantier

warnings.filterwarnings("ignore")


#### Contenu des onglets de paramètres
tab_content_param = dbc.Container(
    [
        html.Br(),
        dt.DataTable(
            id="table_params",
            editable=True,
            filter_action="native",
            fixed_rows={"headers": True},
            style_as_list_view=True,
            style_cell={
                "backgroundColor": "rgb(50, 50, 50)",
                "color": "white",
                "textAlign": "center",
                "whiteSpace": "normal",
                "height": "auto",
                "minWidth": "180px",
                "width": "180px",
                "maxWidth": "180px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
            },
            style_header={
                "backgroundColor": "rgb(20, 20, 20)",
                "color": "white",
                "fontWeight": "bold",
            },
            style_table={"overflowY": "auto"},
        ),
    ]
)

#### Definition des onglets par type de paramètre
tabs_param = html.Div(
    [
        html.Br(),
        dbc.Row(
            dbc.Tabs(
                [
                    dbc.Tab(labelClassName="fas fa-layer-group", tab_id=1),
                    dbc.Tab(labelClassName="fas fa-vector-square", tab_id=2),
                    dbc.Tab(labelClassName="far fa-dot-circle", tab_id=3),
                    dbc.Tab(labelClassName="fas fa-slash", tab_id=4),
                    dbc.Tab(labelClassName="fas fa-arrows-alt-h", tab_id=5),
                    dbc.Tab(labelClassName="fab fa-cloudscale", tab_id=6),
                    dbc.Tab(labelClassName="fas fa-water", tab_id=7),
                ],
                id="tabs_param",
                active_tab=1,
                persistence=True,
                persistence_type="session",
            ),
            justify="center",
        ),
        tab_content_param,
        html.Br(),
        dbc.Row(
            dbc.Button(
                n_clicks=0, id="update_params", className="fas fa-save", size="lg"
            ),
            justify="center",
        ),
        dbc.Row(
            html.Div(
                id="update_success",
                className="text-success",
            ),
            justify="center",
        ),
    ]
)

layout = tabs_param


#### renvoie le tableau de valeurs correpondant à l'onglet sélectionné
#### ainsi que le chantier sélectionné
@app.callback(
    [
        Output("table_params", "data"),
        Output("table_params", "columns"),
    ],
    [
        Input("tabs_param", "active_tab"),
        State("chantier-select", "data"),
    ],
)
def display_table(tab, chantier):
    with engine.connect() as con:
        if tab == 1:

            ''' Paramètre : Chantier'''

            query = f"SELECT * FROM chantier WHERE nom_chantier='{chantier}'"
            parametres = pd.read_sql_query(query, con=con).iloc[:, 1:]
            return parametres.to_dict("records"), [
                {"name": i, "id": i} for i in parametres.columns
            ]
        if tab == 2:

            ''' Paramètre : Secteurs'''

            query1 = f"SELECT * FROM secteur WHERE nom_chantier='{chantier}'"
            query2 = f"SELECT * FROM secteur_param WHERE nom_chantier='{chantier}'"
            gauche = pd.read_sql_query(query1, con=con)[["nom_secteur", "nom_chantier"]]
            droite = pd.read_sql_query(query2, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]
        if tab == 3:

            ''' Paramètre : Cibles'''

            values = memoized_data(
                chantier, "actif", "topographie", "topo.csv"
            ).columns[1:]
            liste_cible = [values[3 * i][:-2] for i in range(len(values) // 3)]
            query = f"select * from cible_param where nom_chantier='{chantier}'"
            gauche = pd.DataFrame.from_dict(
                {
                    "nom_capteur": liste_cible,
                    "nom_chantier": [chantier for i in range(len(liste_cible))],
                }
            )
            droite = pd.read_sql_query(query, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]
        if tab == 4:

            ''' Paramètre : Inclinomètres'''


            query1 = f"SELECT * FROM capteur WHERE nom_chantier='{chantier}' and type='inclino'"
            query2 = f"SELECT * FROM inclino_param WHERE nom_chantier='{chantier}'"
            gauche = pd.read_sql_query(query1, con=con)[["nom_capteur", "nom_chantier"]]
            droite = pd.read_sql_query(query2, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]
        if tab == 5:

            ''' Paramètre : Tirants'''

            query1 = f"SELECT * FROM capteur WHERE nom_chantier='{chantier}' and type='tirant'"
            query2 = f"SELECT * FROM inclino_param WHERE nom_chantier='{chantier}'"
            gauche = pd.read_sql_query(query1, con=con)[["nom_capteur", "nom_chantier"]]
            droite = pd.read_sql_query(query2, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]
        if tab == 6:

            ''' Paramètre : Jauges'''


            query1 = f"SELECT * FROM capteur WHERE nom_chantier='{chantier}' and type='jauge'"
            query2 = f"SELECT * FROM inclino_param WHERE nom_chantier='{chantier}'"
            gauche = pd.read_sql_query(query1, con=con)[["nom_capteur", "nom_chantier"]]
            droite = pd.read_sql_query(query2, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]
        if tab == 7:

            ''' Paramètre : Piezomètres'''


            query1 = f"SELECT * FROM capteur WHERE nom_chantier='{chantier}' and type='piezo'"
            query2 = f"SELECT * FROM inclino_param WHERE nom_chantier='{chantier}'"
            gauche = pd.read_sql_query(query1, con=con)[["nom_capteur", "nom_chantier"]]
            droite = pd.read_sql_query(query2, con=con)
            result = gauche.merge(droite, how="left")
            return result.to_dict("records"), [
                {"name": i, "id": i} for i in result.columns
            ]



#### Mise à jour des paramètres en fonction des modifications renseignées dans le tableau de valeurs
@app.callback(
    Output("update_success", "children"),
    [
        Input("update_params", "n_clicks"),
        State("table_params", "data"),
        State("tabs_param", "active_tab"),
        State("chantier-select", "data"),
        State("update_success", "children"),
    ],
)
def update_params(n_clicks, data, tab, chantier, label):
    if n_clicks:

        '''Conversion des données du tableau en DataFrame'''
        df = pd.DataFrame(data)

        '''Affectation des premières colonnes (index) en clef primaires (SQL)'''
        df = df.set_index([df.columns[0], df.columns[1]])


        ''' La fonction upsert permet de mettre à jour (UPDATE) la table SQL si une valeur correspondants aux clefs
        primaires et modifiée et insert une nouvelle entrée lorsque le couple de clefs primaires n'existe pas encore'''

        if tab == 1:
            df = df.reset_index().set_index("nom_chantier")
            upsert(engine=engine, df=df, table_name="chantier", if_row_exists="update")
        if tab == 2:
            upsert(
                engine=engine, df=df, table_name="secteur_param", if_row_exists="update"
            )
        if tab == 3:
            upsert(
                engine=engine, df=df, table_name="cible_param", if_row_exists="update"
            )
        if tab == 4:
            upsert(
                engine=engine, df=df, table_name="inclino_param", if_row_exists="update"
            )
        if tab == 5:
            upsert(
                engine=engine, df=df, table_name="tirant_param", if_row_exists="update"
            )
        if tab == 6:
            upsert(
                engine=engine, df=df, table_name="jauge_param", if_row_exists="update"
            )
        if tab == 7:
            upsert(
                engine=engine, df=df, table_name="piezo_param", if_row_exists="update"
            )
        return "Les paramètres ont bien été sauvegardés"
    else:
        return ""
