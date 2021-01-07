import warnings
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from data import get_data, export_data
import pandas as pd
from server import app
from config import engine
import dash_table as dt

warnings.filterwarnings("ignore")

profil = 1

tab_content_param = dbc.Container([
            html.Br(),
            dt.DataTable(
                id="table_params",
                editable=True,
                filter_action="native",
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
                    "fontWeight": "bold"},
                page_size=15
                    ),
            dbc.Button(
                children="Mettre à jour les paramètres",
                n_clicks=0,
                id="update_params",
                color="link",
                    ),
            html.Div(
                id='update_success',
                className="text-success",
                    )
                ]

            )

tabs_pram = html.Div(
    [
        dbc.Row(
            id='nav-buttons',
            children=[],
            justify='center'
        ),
        html.Br(),
        dbc.Tabs(
            [
                dbc.Tab(label="Paramètres généraux", tab_id="tab-param"),
                dbc.Tab(label="Cibles", tab_id="tab-topo"),
                dbc.Tab(label="Inclinomètres", tab_id="tab-inclino"),
                dbc.Tab(label="Tirants", tab_id="tab-tirant"),
                dbc.Tab(label="Piezometres", tab_id="tab-piezo"),
                dbc.Tab(label="Jauges", tab_id="tab-jauge"),
                dbc.Tab(label="Butons", tab_id="tab-buton"),
            ],
            id="tabs_param",
            active_tab="tab-param",
        ),
        tab_content_param,
    ]
)

layout = tabs_pram

@app.callback(
    Output('nav-buttons','children'),
    Input('page-content', 'children'))
def options_buttons(content):
    if profil==1:
        return [
                dbc.Button('Chantier', color = 'dark', className="mr-1", href='/chantier'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Admin', id= 'profil', color='dark', className="mr-1", href='admin'),
                dbc.Button('Export PDF', color = 'light', className="mr-1"),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')]
    else :
        return [
                dbc.Button('Chantier', color = 'dark', className="mr-1", href='/chantier'),
                dbc.Button('Profil', color = 'dark', className="mr-1", href='/profil'),
                dbc.Button('Export PDF', color = 'light', className="mr-1"),
                dbc.Button('Déconnexion', color = 'dark', className="mr-1", href='/logout')]


@app.callback(
    [
        Output("table_params", "data"),
        Output("table_params", "columns"),
        ],
    [
        Input("chantier-store", "data"),
        Input("tabs_param", "active_tab"),
        ]
)
def update_table(chantier, tab):
    with engine.connect() as con:
        if tab == 'tab-param':
            parametres = get_data(chantier, 'paramètres', 'parametres_generaux.csv', sep=False)
        if tab == 'tab-topo':
            parametres = pd.read_sql('cible_param', con=con)
        if tab == 'tab-inclino':
            parametres = pd.read_sql('inclino_param', con=con)
        if tab == 'tab-tirant':
            parametres = pd.read_sql('tirant_param', con=con)
        if tab == 'tab-piezo':
            parametres = pd.read_sql('piezo_param', con=con)
        if tab == 'tab-jauge':
            parametres = pd.read_sql('jauge_param', con=con)
        if tab == 'tab-buton':
            parametres = pd.read_sql('buton_param', con=con)
    return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]


@app.callback(
    Output('update_success', 'children'),
    [
        Input("table_params", "data"),
        Input('update_params', 'n_clicks'),
        Input("chantier-store", "data"),
    ]
)
def update_params(data, n_clicks, chantier):
    if n_clicks>0:
        df = pd.DataFrame(data)
        export_data(df, chantier, 'paramètres', 'parametres_generaux.csv')
        return 'Les paramètres ont bien été sauvegardés'
    else:
        return ''
