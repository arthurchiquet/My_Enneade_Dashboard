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
from pangres import upsert

warnings.filterwarnings("ignore")

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
                'whiteSpace': 'normal',
                'height': 'auto',
                'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            style_header={
                "backgroundColor": "rgb(20, 20, 20)",
                "color": "white",
                "fontWeight": "bold",
            },
            style_table={"overflowY": "auto"},
        )
    ]
)

tabs_pram = html.Div(
    [
        html.Br(),
        dbc.Row(
            dbc.Tabs(
                [

                    dbc.Tab(labelClassName="fas fa-layer-group", tab_id=1),
                    dbc.Tab(labelClassName="fas fa-vector-square", tab_id=2),
                    # dbc.Tab(labelClassName="far fa-dot-circle", tab_id=3),
                    dbc.Tab(labelClassName="fas fa-slash", tab_id=4),
                    dbc.Tab(labelClassName="fas fa-arrows-alt-h", tab_id=5),
                    dbc.Tab(labelClassName="fab fa-cloudscale", tab_id=6),
                    dbc.Tab(labelClassName="fas fa-water", tab_id=7),
                ],
                id="tabs_param",
                active_tab=1,
            ),
            justify="center",
        ),
        tab_content_param,
        html.Br(),
        dbc.Row(
            dbc.Button(
                n_clicks=0,
                id="update_params",
                className='fas fa-save',
                size='lg'
            ), justify='center'
        ),
        dbc.Row(
            html.Div(
                id="update_success",
                className="text-success",
            ), justify='center'
        )
    ]
)

layout = tabs_pram


@app.callback(
    [
        Output("table_params", "data"),
        Output("table_params", "columns"),
    ],
    [
        Input("tabs_param", "active_tab"),
        State("chantier-select", "data"),
        State("global-params", "data")
    ],
)
def display_table(tab, chantier, data):
    with engine.connect() as con:
        if tab == 1:
            query=f"SELECT * FROM chantier WHERE nom_chantier='{chantier}'"
            parametres = pd.read_sql_query(query, con=con).iloc[:,1:]
            return parametres.to_dict("records"), [{"name": i, "id": i} for i in parametres.columns]
        if tab == 2:
            query = f"SELECT * FROM secteur_param WHERE nom_chantier='{chantier}'"
            sql_result = pd.read_sql_query(query, con=con)
            parametres = pd.DataFrame({'secteur':data['secteur'].keys(), 'nom_chantier': chantier})
            result=parametres.merge(sql_result, how='left')
            return result.to_dict("records"), [{"name": i, "id": i} for i in result.columns]

        # if tab == 3:
        #     filtre_secteur = tuple(params[params.type == "cible"].capteur)
        #     query = f"select * from cible_param where cible in {filtre_secteur}"
        #     parametres = pd.read_sql_query(query, con=con)

        if tab == 4:
            query = f"select * from inclino_param WHERE nom_chantier='{chantier}'"
            sql_result = pd.read_sql_query(query, con=con)
            parametres = pd.DataFrame({'inclino':data['inclino'].keys(), 'nom_chantier': chantier})
            result=parametres.merge(sql_result, how='left')
            return result.to_dict("records"), [{"name": i, "id": i} for i in result.columns]
        if tab == 5:
            query = f"select * from tirant_param WHERE nom_chantier='{chantier}'"
            sql_result = pd.read_sql_query(query, con=con)
            parametres = pd.DataFrame({'tirant':data['tirant'].keys(), 'nom_chantier': chantier})
            result=parametres.merge(sql_result, how='left')
            return result.to_dict("records"), [{"name": i, "id": i} for i in result.columns]
        if tab == 6:
            query = f"select * from jauge_param WHERE nom_chantier='{chantier}'"
            sql_result = pd.read_sql_query(query, con=con)
            parametres = pd.DataFrame({'jauge':data['jauge'].keys(), 'nom_chantier': chantier})
            result=parametres.merge(sql_result, how='left')
            return result.to_dict("records"), [{"name": i, "id": i} for i in result.columns]
        if tab == 7:
            query = f"select * from piezo_param WHERE nom_chantier='{chantier}'"
            sql_result = pd.read_sql_query(query, con=con)
            parametres = pd.DataFrame({'piezo':data['piezo'].keys(), 'nom_chantier': chantier})
            result=parametres.merge(sql_result, how='left')
            return result.to_dict("records"), [{"name": i, "id": i} for i in result.columns]


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
        df = pd.DataFrame(data)
        df = df.set_index([df.columns[0], df.columns[1]])
        if tab ==1:
            pass
        if tab ==2:
            upsert(engine=engine,
                df=df,
                table_name='secteur_param',
                if_row_exists='update'
            )
        if tab ==4:
            upsert(engine=engine,
                df=df,
                table_name='inclino_param',
                if_row_exists='update'
            )
        if tab ==5:
            upsert(engine=engine,
                df=df,
                table_name='tirant_param',
                if_row_exists='update'
            )
        if tab ==6:
            upsert(engine=engine,
                df=df,
                table_name='jauge_param',
                if_row_exists='update'
            )
        if tab ==7:
            upsert(engine=engine,
                df=df,
                table_name='piezo_param',
                if_row_exists='update'
            )
        return "Les paramètres ont bien été sauvegardés"
    else:
        return ""
