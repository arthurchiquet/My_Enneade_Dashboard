#### import des modules dash

import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table as dt

#### Import des librairies

from flask_login import current_user
import warnings
from datetime import date
import pandas as pd
import base64
import io

from config import engine
from server import app
from data import export_data

warnings.filterwarnings("ignore")

user = "Vallicorp"

tab_content = dbc.Container(
    fluid=True,
    children=[
        html.Div(
            [
                html.Br(),
                dbc.Row(html.H3("Importer un document"), justify="center"),
                html.Br(),
                dbc.Row(
                    dcc.Dropdown(
                        id="choix_chantier",
                        placeholder="Selectionner un chantier",
                        style={"color": "black", "width": "300px"},
                        clearable=False,
                    ),
                    justify="center",
                ),
                html.Br(),
                dbc.Row(
                    dcc.Dropdown(
                        id="type_document",
                        placeholder="Type de données",
                        style={"color": "black", "width": "300px"},
                        options=[
                            {"label": "Mesures topographiques", "value": 1},
                            {"label": "Mesures inclinométriques", "value": 2},
                            {"label": "Mesures piezométriques", "value": 3},
                            {"label": "Charges tirants", "value": 4},
                            {"label": "Jauges", "value": 5},
                        ],
                        clearable=False,
                    ),
                    justify="center",
                ),
                html.Br(),
                dbc.Row(
                    dbc.Input(
                        id="nom_capteur",
                        placeholder="Nom du capteur",
                        style={"display": "none"},
                    ),
                    justify="center",
                ),
                html.Br(),
                dbc.Row(html.H6("Date de la dernière mesure"), justify="center"),
                dbc.Row(
                    dcc.DatePickerSingle(
                        id="date-picker",
                        initial_visible_month=date.today(),
                        placeholder="             Saisir une date",
                    ),
                    justify="center",
                ),
                html.Br(),
                dbc.Row(
                    dcc.Upload(
                        id="datatable-upload",
                        children=html.Div(
                            [html.A("Séléctionner un fichier (XLS ou CSV)")]
                        ),
                        max_size=-1,
                        style={
                            "width": "300px",
                            "height": "60px",
                            "lineHeight": "60px",
                            "borderWidth": "1px",
                            "borderStyle": "dashed",
                            "borderRadius": "5px",
                            "textAlign": "center",
                            "margin": "10px",
                        },
                    ),
                    justify="center",
                ),
                html.Br(),
                dt.DataTable(
                    id="datatable-upload-container",
                    style_cell={
                        "backgroundColor": "rgb(50, 50, 50)",
                        "color": "white",
                        # 'minWidth': '150px',
                        # 'width': '150px',
                        # 'maxWidth': '150px',
                        "textAlign": "center",
                    },
                    style_header={
                        "backgroundColor": "rgb(20, 20, 20)",
                        "color": "white",
                        "fontWeight": "bold",
                    },
                ),
                dbc.Row(
                    dbc.Button(
                        id="update", n_clicks=0, className="fas fa-save", size="lg"
                    ),
                    justify="center",
                ),
                dbc.Tooltip("Enregistrer", target="update", placement="down"),
                html.Br(),
                dbc.Row(
                    html.Div(
                        id="import_success",
                        className="text-success",
                    ),
                    justify="center",
                ),
            ]
        )
    ],
)

tabs = tab_content

layout = tabs


#### Appelle la fonction de lecture CSV ou Excel en fonction du format
#### et retourne le resultat sous forme de DataFrame
def read_data(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if "csv" in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode("utf-8")), sep=None, engine="python"
        )

    elif "xls" in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded), sep=None, engine="python")


#### Retourne la liste des chantiers accessibles par l'utilisateur connecté
@app.callback(
    Output("choix_chantier", "options"),
    Input("page-content", "children"))
def update_choix_chantier(page):
    with engine.connect() as con:
        query = f"SELECT * FROM chantier where username = '{user}'"
        liste_chantiers = pd.read_sql_query(query, con=con).nom_chantier.tolist()
    if len(liste_chantiers) == 0:
        return []
    else:
        return [{"label": chantier, "value": chantier} for chantier in liste_chantiers]


#### Affiche une zone de saisie supplémentaire dans le cas de l'import de données
#### pour inclinomètre ou piezomètre
@app.callback(
    Output("nom_capteur", "style"),
    Input("type_document", "value"))
def prop_nom_capteur(type_doc):
    if type_doc in [2, 3]:
        return {"display": "inline-block", "color": "black", "width": "300px"}
    else:
        return {"display": "none"}


#### Affiche une partie du fichier téléchargé sous forme d'une table de données
#### pour confirmer le format des colonnes et données
@app.callback(
    Output("datatable-upload-container", "data"),
    Output("datatable-upload-container", "columns"),
    Input("datatable-upload", "contents"),
    State("datatable-upload", "filename"),
)
def update_table(contents, filename):
    if contents is None:
        return [{}], []
    df = read_data(contents, filename).iloc[-5:, :10]
    return df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]



#### Importe et remplace la dernière version ACTIF des données et enregistre une version
#### historisée à la date renseignée dans ARCHIVE (dans la bucket Google Cloud Storage)
@app.callback(
    Output("import_success", "children"),
    Input("update", "n_clicks"),
    State("datatable-upload", "filename"),
    State("datatable-upload", "contents"),
    State("choix_chantier", "value"),
    State("type_document", "value"),
    State("nom_capteur", "value"),
    State("date-picker", "date"),
)
def import_file(n_clicks, filename, contents, chantier, type_doc, nom_capteur, date):
    if n_clicks > 0:
        if contents is None:
            return ""
        else:
            df = read_data(contents, filename)
            if type_doc == 1:

                '''type : mesures topographiques globales'''

                filename_archive = f"topo_{date}.csv"
                filename_actif = "topo.csv"
                export_data(df, chantier, "actif", "topographie", filename_actif)
                export_data(df, chantier, "archive", "topographie", filename_archive)
            elif type_doc == 2:

                '''type : mesures associées à UN inclinomètre defini'''

                filename_archive = f"{nom_capteur}_{date}.csv"
                filename_actif = f"{nom_capteur}.csv"
                export_data(df, chantier, "actif", "inclinometrie", filename_actif)
                export_data(df, chantier, "archive", "inclinometrie", filename_archive)
            elif type_doc == 3:

                '''type : mesures associées à UN piezomètre defini '''

                filename_archive = f"{nom_capteur}_{date}.csv"
                filename_actif = f"{nom_capteur}.csv"
                export_data(df, chantier, "actif", "piezometrie", filename_actif)
                export_data(df, chantier, "archive", "piezometrie", filename_archive)
            elif type_doc == 4:

                '''type : mesures tirant globales'''

                filename_archive = f"tirant_{date}.csv"
                filename_actif = "tirant.csv"
                export_data(df, chantier, "actif", "tirant", filename_actif)
                export_data(df, chantier, "archive", "tirant", filename_archive)
            elif type_doc == 5:

                '''type : mesures jauge globales'''

                filename_archive = f"jauge_{date}.csv"
                filename_actif = "jauge.csv"
                export_data(df, chantier, "actif", "jauge", filename_actif)
                export_data(df, chantier, "archive", "jauge", filename_archive)
            return "Le fichier à bien été importé"
    else:
        return ""
