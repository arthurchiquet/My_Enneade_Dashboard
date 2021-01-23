import warnings
from datetime import date
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from datetime import date
import pandas as pd
from server import app
from data import export_data
import dash_table as dt
import base64
import io

warnings.filterwarnings("ignore")

tab_content = dbc.Container(
    fluid=True,
    children=[
        html.Div(
            [
                dcc.Upload(
                    id="datatable-upload",
                    children=html.Div([html.A("Séléctionner un fichier (XLS ou CSV)")]),
                    style={
                        "width": "100%",
                        "height": "60px",
                        "lineHeight": "60px",
                        "borderWidth": "1px",
                        "borderStyle": "dashed",
                        "borderRadius": "5px",
                        "textAlign": "center",
                        "margin": "10px",
                    },
                ),
                html.Br(),
                dt.DataTable(
                    id="datatable-upload-container",
                    style_cell={
                        'backgroundColor': 'rgb(50, 50, 50)',
                        'color': 'white',
                        # 'minWidth': '150px',
                        # 'width': '150px',
                        # 'maxWidth': '150px',
                        'textAlign': 'center'
                    },
                    style_header={
                        'backgroundColor': 'rgb(20, 20, 20)',
                        'color': 'white',
                        "fontWeight": "bold"
                    }
                ),
                html.Br(),
                dcc.Dropdown(
                    id="choix_chantier",
                    style={'color':'black'},
                    options=[
                        {"label":'Chantier 1', "value":"chantier_1"},
                        {"label":'Chantier 2', "value":"chantier_2"}
                    ],
                    clearable=False,
                ),
                html.Br(),
                dcc.Dropdown(
                    id="type_document",
                    style={'color':'black'},
                    options=[
                        {"label": "Mesures topographiques", "value": "topo"},
                        {"label": "Mesures inclinométriques", "value": "inclino"},
                        {"label": "Mesures piezométriques", "value": "jauges"},
                        {"label": "Charges tirants", "value": "tirants"},
                        {"label": "Charges butons", "value": "butons"},
                        {"label": "Jauges", "value": "jauges"},
                    ],
                ),
                html.Br(),
                dcc.DatePickerSingle(
                    id='date-picker',
                    initial_visible_month=date.today(),
                    date=date.today()
                ),
                html.Br(),
                html.Hr(),
                dbc.Button("Mettre à jour", id="update", n_clicks=0),
                html.Br(),
                html.Div(
                    id='import_success',
                    className="text-success",
                        )
            ]
        )
    ],
)

tabs = tab_content

layout = tabs

# @app.callback(
#     Output("choix_chantier", "options"),
#     [Input("chantier", "options")])
# def chantiers(chantier):
#     return chantier

def read_data(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    if "csv" in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(io.StringIO(decoded.decode("utf-8")), sep=';').iloc[-5:,:10]
    elif "xls" in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded), sep=';').iloc[-5:,:10]

@app.callback(
    Output("datatable-upload-container", "data"),
    Output("datatable-upload-container", "columns"),
    Input("datatable-upload", "contents"),
    State("datatable-upload", "filename"),
)
def update_table(contents, filename):
    if contents is None:
        return [{}], []
    df = read_data(contents, filename)
    return df.to_dict("records"), [{"name": i, "id": i} for i in df.columns]

@app.callback(
    Output("import_success", "children"),
   [Input("datatable-upload", "contents"),
    Input('choix_chantier', 'value'),
    Input('type_document', 'value'),
    Input('date-picker', 'date'),
    Input('update', 'n_clicks')],
    State("datatable-upload", "filename"),
)
def import_file(contents, chantier, type_doc, date, n_clicks, filename):
    if n_clicks > 0 :
        if contents is None:
            return ''
        df = read_data(contents, filename)
        filename_histo =f'{type_doc}_{date}.csv'
        filename_actif =f'{type_doc}.csv'
        export_data(df, chantier, 'historique', filename_histo)
        export_data(df, chantier, 'actif', filename_actif)
        return 'Le fichier à bien été importé'
    else:
        return ''
