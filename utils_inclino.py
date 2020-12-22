import pandas as pd
import numpy as np
import io
from server import app
import dash_table as dt
from config import engine
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import get_data
import warnings

colors = {
    'background': '#222222',
    'text': 'white'
}

def graph_inclino(chantier, inclino):
    dfnorm = get_data(chantier, 'actif', f'{inclino}_norm.csv', sep=False)
    dftan = get_data(chantier, 'actif', f'{inclino}_tan.csv', sep=False)
    last_col = dfnorm.columns[-1]
    past_last_col = dfnorm.columns[-2]
    dfnorm[f'{last_col} vs {past_last_col}'] = dfnorm[last_col] - dfnorm[past_last_col]
    dftan[f'{last_col} vs {past_last_col}'] = dftan[last_col] - dftan[past_last_col]
    fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=["Déplacements normaux (mm)", "Déplacements tangentiels (mm)"],
        )
    fig.add_trace(go.Scatter(name=last_col, x=dfnorm[last_col], y=dfnorm.profondeur), row=1, col=1)
    fig.add_trace(go.Scatter(name=f'{last_col} vs {past_last_col}', x=dfnorm[f'{last_col} vs {past_last_col}'], y=dfnorm.profondeur), row=2, col=1)
    fig.add_trace(go.Scatter(name=last_col, x=dftan[last_col], y=dftan.profondeur), row=2, col=1)
    fig.add_trace(go.Scatter(name=f'{last_col} vs {past_last_col}', x=dftan[f'{last_col} vs {past_last_col}'], y=dftan.profondeur), row=1, col=1)
    fig.update_xaxes(range=[-10, 25], showgrid=False)
    fig.update_yaxes(autorange="reversed", matches=None, showgrid=False)
    fig.update_layout(
        legend_title_text=None,
        yaxis_title="Profondeur (m)",
        xaxis_title=None,
        height=600,
        legend_orientation='h',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin={"r":0,"t":20,"l":0,"b":0})
    return fig


warnings.filterwarnings("ignore")


profondeurs_table = [
    "Date",
    "2.0",
    "5.0",
    "10.0",
    "20.0",
    "30.0",
    "40.0",
    "50.0",
    "60.0",
]

controls1 = dcc.Slider(
    id="nb_curv",
    min=1,
    max=10,
    step=1,
    value=5,
    dots=True,
    marks={
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
    },
)

controls2 = dcc.Slider(
    id="nb_curv2",
    min=1,
    max=10,
    step=1,
    value=5,
    dots=True,
    marks={
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
    },
)

controls3 = dcc.Slider(
    id="nb_curv3",
    min=1,
    max=10,
    step=1,
    value=1,
    dots=True,
    marks={
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
    },
)

controls4 = dcc.Slider(
    id="prof",
    min=2,
    max=60,
    value=2,
    dots=True,
    marks={
        2: "2",
        5: "5",
        10: "10",
        20: "20",
        30: "30",
        40: "40",
        50: "50",
        60: "60",
    },
)

controls3D = dcc.Slider(
    id="nb_curv3d",
    min=1,
    max=10,
    step=1,
    value=1,
    dots=True,
    marks={
        1: "1",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
    },
)

table_norm = dt.DataTable(
    id="table_norm",
    columns=[{"name": i, "id": i} for i in profondeurs_table],
    style_cell_conditional=[
        {"if": {"column_id": c}, "textAlign": "center"} for c in profondeurs_table
    ],
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
    ],
    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
)

table_tan = dt.DataTable(
    id="table_tan",
    columns=[{"name": i, "id": i} for i in profondeurs_table],
    style_cell_conditional=[
        {"if": {"column_id": c}, "textAlign": "center"} for c in profondeurs_table
    ],
    style_data_conditional=[
        {"if": {"row_index": "odd"}, "backgroundColor": "rgb(248, 248, 248)"}
    ],
    style_header={"backgroundColor": "rgb(230, 230, 230)", "fontWeight": "bold"},
)

inclino_content = html.Div(
        [
        html.Br(),
        dbc.Container([
            dcc.Graph(
                id="inclino_3d",
                config={"scrollZoom": True}
                ),
            dbc.Label("Affichage historique (nombre de courbes)"),
            controls3D,
            ]),
        html.Br(),
        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Card(
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="var_norm",
                                                                config={
                                                                    "scrollZoom": True
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="var_tan",
                                                                config={
                                                                    "scrollZoom": True
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            dbc.Label(
                                                "Affichage historique (nombre de courbes)"
                                            ),
                                            controls3,
                                        ],
                                    ),
                                    html.Div(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="var_norm_2",
                                                                config={
                                                                    "scrollZoom": True
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                    dbc.Col(
                                                        [
                                                            dcc.Graph(
                                                                id="var_tan_2",
                                                                config={
                                                                    "scrollZoom": True
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            ),
                                            dbc.Label(
                                                "Affichage historique (nombre de courbes)"
                                            ),
                                            controls1,
                                        ],
                                    ),
                                ]
                            ),
                            body=True,
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Card(
                            html.Div(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="var_norm_3",
                                                        config={"scrollZoom": True},
                                                    ),
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="var_tan_3",
                                                        config={"scrollZoom": True},
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    dbc.Label(
                                        "Affichage historique (nombre de courbes)"
                                    ),
                                    controls2,
                                ],
                            ),
                            body=True,
                        ),
                    ]
                ),
                html.Br(),
                dbc.Row(
                    [
                        dbc.Card(
                            html.Div(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="var_norm_4",
                                                        config={"scrollZoom": True},
                                                    ),
                                                ]
                                            ),
                                            dbc.Col(
                                                [
                                                    dcc.Graph(
                                                        id="var_tan_4",
                                                        config={"scrollZoom": True},
                                                    ),
                                                ]
                                            ),
                                        ]
                                    ),
                                    dbc.Label("Choix de la profondeur (m)"),
                                    controls4,
                                ],
                            ),
                            body=True,
                        )
                    ]
                ),
                html.Hr(),
                dcc.Markdown(
                    """**Composante normale "n" (mm) en fonction de la profondeur (m)**"""
                ),
                table_norm,
                html.Br(),
                dcc.Markdown(
                    """**Composante tangentielle "t" (mm)  en fonction de la profondeur (m)**"""
                ),
                table_tan,
            ]
        ),
    ]
)

@app.callback(
    [
        Output("var_norm", "figure"),
        Output("var_tan", "figure"),
        Output("var_norm_2", "figure"),
        Output("var_tan_2", "figure"),
        Output("inclino_3d", "figure"),
        Output("var_norm_3", "figure"),
        Output("var_tan_3", "figure"),
        Output("var_norm_4", "figure"),
        Output("var_tan_4", "figure"),
        Output("table_norm", "data"),
        Output("table_tan", "data"),
    ],
    [
        Input("secteur-store", "data"),
        Input("nb_curv", "value"),
        Input("nb_curv2", "value"),
        Input("nb_curv3", "value"),
        Input("nb_curv3d", "value"),
        Input("prof", "value"),
        Input("chantier-store", "data"),
    ]
)
def update_graphs(secteur, nb_courbes, nb_courbes2, nb_courbes3, nb_courbes_3D, profondeur, chantier):
    try:
        dfnorm = get_data(chantier, 'actif', f'{inclino}_norm.csv', sep=False)
        dftan = get_data(chantier, 'actif', f'{inclino}_tan.csv', sep=False)
        fig1 = create_graph_1(dfnorm, chantier, inclino, nb_courbes3)
        fig1.update_layout(title="Déplacements normaux (mm)")
        fig2 = create_graph_1(dftan, chantier, inclino, nb_courbes3)
        fig2.update_layout(title="Déplacements tangentiels (mm)")
        fig3 = create_graph_2(dfnorm, chantier, inclino, nb_courbes)
        fig3.update_layout(title="Déplacements normaux (mm)")
        fig4 = create_graph_2(dftan, chantier, inclino, nb_courbes)
        fig4.update_layout(title="Déplacements tangentiels (mm)")
        fig5 = create_3d_graph(dfnorm, dftan, chantier, inclino, nb_courbes_3D)
        fig6 = create_graph_3(dfnorm, chantier, inclino, nb_courbes2)
        fig6.update_layout(title="Déplacements normaux ponctuels (mm)")
        fig7 = create_graph_3(dftan, chantier, inclino, nb_courbes2)
        fig7.update_layout(title="Déplacements tangentiels ponctuels (mm)")
        fig8 = create_graph_4(dfnorm, chantier, inclino, profondeur)
        fig8.update_layout(title="Evolution des déplacements normaux (mm)")
        fig9 = create_graph_4(dftan, chantier, inclino, profondeur)
        fig9.update_layout(title="Evolution des déplacements tangentiels (mm)")
        tablenorm = dfnorm.set_index("profondeur").T[[2, 5, 10, 20, 30, 40, 50, 60]].iloc[-15:, :]
        tablenorm = tablenorm.reset_index().rename(columns={"index": "Date"})
        tabletan = dftan.set_index("profondeur").T[[2, 5, 10, 20, 30, 40, 50, 60]].iloc[-15:, :]
        tabletan = tabletan.reset_index().rename(columns={"index": "Date"})
        return fig1, fig2, fig3, fig4, fig5,fig6, fig7, fig8, fig9, tablenorm.to_dict("rows"), tabletan.to_dict("rows")
    except:
        return {}, {}, {}, {}, {}, {}, {}, {}, {}, [],[]
