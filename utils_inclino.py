#### import des modules dash

import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

#### Import des librairies python
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings


from server import app
from config import engine
from utils_maps import empty_figure
from data import get_data


colors = {"background": "#222222", "text": "white"}

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


#### Slider permettant de choisir le nombre de courbes à afficher (entre 1 et 10)
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

#### Slider permettant de choisir le nombre de courbes à afficher (entre 1 et 10)
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

#### Slider permettant de choisir le nombre de courbes à afficher (entre 1 et 10)
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

#### Slider permettant de choisir le nombre de courbes à afficher (entre 1 et 10)
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

#### Definition de la table des déplacements normaux
table_norm = dt.DataTable(
    id="table_norm",
    columns=[{"name": i, "id": i} for i in profondeurs_table],
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
)


#### Definition de la table des déplacements tangentiels
table_tan = dt.DataTable(
    id="table_tan",
    columns=[{"name": i, "id": i} for i in profondeurs_table],
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
)

layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_norm",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_tan",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                    ]
                ),
                html.Br(),
                dbc.Label("Affichage historique (nombre de courbes)"),
                controls3,
                html.Br(),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_norm_2",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="inclino_3d",
                                    config={"scrollZoom": True},
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_tan_2",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                    ]
                ),
                html.Br(),
                dbc.Label("Affichage historique (nombre de courbes)"),
                controls1,
            ],
            className="jumbotron",
            fluid=True,
        ),
        html.Br(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_norm_3",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_tan_3",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                    ]
                ),
                html.Br(),
                dbc.Label("Affichage historique (nombre de courbes)"),
                controls2,
            ],
            className="jumbotron",
            fluid=True,
        ),
        html.Br(),
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_norm_4",
                                    figure=empty_figure(),
                                ),
                            ]
                        ),
                        dbc.Col(
                            [
                                dcc.Graph(
                                    id="var_tan_4",
                                    figure=empty_figure(),
                                )
                            ]
                        ),
                    ]
                ),
                html.Br(),
                dbc.Label("Choix de la profondeur (m)"),
                controls4,
            ],
            className="jumbotron",
            fluid=True,
        ),
        dbc.Container(
            [
                dcc.Markdown(
                    """**Composante normale "n" (mm) en fonction de la profondeur (m)**"""
                ),
                table_norm,
                html.Br(),
                dcc.Markdown(
                    """**Composante tangentielle "t" (mm)  en fonction de la profondeur (m)**""",
                ),
                table_tan,
            ],
            className="jumbotron",
            fluid=True,
        ),
    ]
)




#### Mise a jour de l'ensemble des graphs et tables de données
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
        Input("secteur-select", "data"),
        Input("nb_curv", "value"),
        Input("nb_curv2", "value"),
        Input("nb_curv3", "value"),
        Input("prof", "value"),
        Input("chantier-select", "data"),
    ],
)
def update_graphs(
    secteur_selected, nb_courbes, nb_courbes2, nb_courbes3, profondeur, chantier
):
    try:

        ''' Extraction du nom de l'inclino se trouvant dans le secteur sélectionné'''

        inclino = secteur_selected["inclino"]

        ''' Telechargement des données normales et tangentielles associées à l'inclino'''

        dfnorm = get_data(
            chantier, "actif", "inclinometrie", f"{inclino}_norm.csv", sep=False
        )
        dftan = get_data(
            chantier, "actif", "inclinometrie", f"{inclino}_tan.csv", sep=False
        )


        ''' Creation de l'ensemble des figure et tables (voir méthodes ci-dessous'''

        fig1 = create_graph_1(dfnorm, chantier, inclino, nb_courbes3, "normal")
        fig2 = create_graph_1(dftan, chantier, inclino, nb_courbes3, "tangentiel")
        fig3 = create_graph_2(dfnorm, chantier, inclino, nb_courbes, "normal")
        fig4 = create_graph_2(dftan, chantier, inclino, nb_courbes, "tangentiel")
        fig5 = create_3d_graph(dfnorm, dftan, chantier, inclino, nb_courbes)
        fig6 = create_graph_3(dfnorm, chantier, inclino, nb_courbes2, "normal")
        fig7 = create_graph_3(dftan, chantier, inclino, nb_courbes2, "tangentiel")
        fig8 = create_graph_4(dfnorm, chantier, inclino, profondeur, "normal")
        fig9 = create_graph_4(dftan, chantier, inclino, profondeur, "tangentiel")
        tablenorm = (
            dfnorm.set_index("profondeur")
            .T[[2, 5, 10, 20, 30, 40, 50, 60]]
            .iloc[-15:, :]
        )
        tablenorm = tablenorm.reset_index().rename(columns={"index": "date"})
        tabletan = (
            dftan.set_index("profondeur")
            .T[[2, 5, 10, 20, 30, 40, 50, 60]]
            .iloc[-15:, :]
        )
        tabletan = tabletan.reset_index().rename(columns={"index": "date"})
        return (
            fig1,
            fig2,
            fig3,
            fig4,
            fig5,
            fig6,
            fig7,
            fig8,
            fig9,
            tablenorm.to_dict("rows"),
            tabletan.to_dict("rows"),
        )
    except:
        return (
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            empty_figure(),
            [],
            [],
        )


#### Methode d'affichage des courbes inclino (UNIQUEMENT DANS LA PAGE CHANTIER)
#### lorqu'un inclino est selectionné sur la carte
def graph_inclino(chantier, inclino, height=None):

    ''' Telechargement des données normales et tangentielles associées à l'inclino'''

    dfnorm = get_data(
        chantier, "actif", "inclinometrie", f"{inclino}_norm.csv", sep=False
    )
    dftan = get_data(
        chantier, "actif", "inclinometrie", f"{inclino}_tan.csv", sep=False
    )

    ''' identification de la derniere mesure connue ainsi que de l'avant dernière'''
    last_col = dfnorm.columns[-1]
    past_last_col = dfnorm.columns[-2]

    ''' creation d'une nouvelle mesure correpondant à la differences des deux mesures ci-dessus'''

    dfnorm[f"{last_col} vs {past_last_col}"] = dfnorm[last_col] - dfnorm[past_last_col]
    dftan[f"{last_col} vs {past_last_col}"] = dftan[last_col] - dftan[past_last_col]

    ''' initialisation de deux sous graphiques sur deux lignes'''

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        shared_yaxes=True,
        vertical_spacing=0.1,
        subplot_titles=["Déplacements normaux (mm)", "Déplacements tangentiels (mm)"],
    )

    ''' premier graph (deplacements normaux) : derniere mesure + difference '''

    fig.add_trace(
        go.Scatter(name=last_col, x=dfnorm[last_col], y=dfnorm.profondeur), row=1, col=1
    )
    fig.add_trace(
        go.Scatter(
            name=f"{last_col} vs {past_last_col}",
            x=dfnorm[f"{last_col} vs {past_last_col}"],
            y=dfnorm.profondeur,
        ),
        row=2,
        col=1,
    )

    ''' premier graph (deplacements tangentiels) : derniere mesure. + difference'''

    fig.add_trace(
        go.Scatter(name=last_col, x=dftan[last_col], y=dftan.profondeur), row=2, col=1
    )
    fig.add_trace(
        go.Scatter(
            name=f"{last_col} vs {past_last_col}",
            x=dftan[f"{last_col} vs {past_last_col}"],
            y=dftan.profondeur,
        ),
        row=1,
        col=1,
    )
    fig.update_yaxes(autorange="reversed", gridcolor="grey")
    fig.update_xaxes(gridcolor="grey")
    fig.update_layout(
        height=height,
        legend_title_text=None,
        yaxis_title="Profondeur (m)",
        xaxis_title=None,
        legend_orientation="h",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 20, "t": 30, "l": 0, "b": 0},
    )
    return fig


####  Creation du graph -> derniere mesure + difference des n dernieres mesures avec la derniere
def create_graph_1(dfi, chantier, inclino, nb_courbes, title):

    ''' trace la derniere mesure en date de l'inclino
    ainsi que la difference entre les n dernieres mesures'''

    df = dfi.copy()
    last_col = df.columns[-1]
    n_col = df.columns[-(1 + nb_courbes)]
    df[f"{last_col} vs {n_col}"] = df[last_col] - df[n_col]
    fig = px.line(
        df,
        y="profondeur",
        x=[last_col, f"{last_col} vs {n_col}"],
        color_discrete_sequence=["red", "green"],
        title=f"Deplacement {title} (mm)",
    )
    fig.update_xaxes(range=[-10, 25])
    fig.update_yaxes(autorange="reversed")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        legend_title_text=None,
        height=400,
        yaxis_title="Profondeur (m)",
        xaxis_title=None,
        legend_orientation="h",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    fig.update_xaxes(gridcolor="grey")
    fig.update_yaxes(gridcolor="grey")
    return fig

#### Creation du graph -> n derniere mesures
def create_graph_2(dfi, chantier, inclino, nb_courbes, title):

    ''' trace les n dernieres mesures de l'inclino'''

    df = dfi.copy()
    cols = df.columns[-nb_courbes:]
    fig = px.line(df, y="profondeur", x=cols, title=f"Deplacement {title} (mm)")
    fig.update_xaxes(range=[-10, 25])
    fig.update_yaxes(autorange="reversed")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        height=400,
        legend_title_text=None,
        legend_traceorder="reversed",
        yaxis_title="Profondeur (m)",
        xaxis_title=None,
        legend_orientation="h",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    fig.update_xaxes(gridcolor="grey")
    fig.update_yaxes(gridcolor="grey")
    return fig

#### creation du graph -> n dernieres deplacmeents ponctuels
def create_graph_3(dfi, chantier, inclino, nb_courbes, title):

    ''' trace les n dernieres deplacements ponctuels de l'inclino'''

    df = dfi.copy()
    cols = df.columns[-nb_courbes:]
    for col in cols:
        df[col] = [0] + [
            df[col].iloc[i + 1] - df[col].iloc[i] for i in range(df.shape[0] - 1)
        ]
    fig = px.line(
        df.reset_index(),
        y="profondeur",
        x=cols,
        title=f"Deplacement ponctuel {title} (mm)",
    )
    fig.update_xaxes(range=[-10, 25])
    fig.update_yaxes(autorange="reversed")
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        height=400,
        legend_title_text=None,
        yaxis_title="Profondeur (m)",
        xaxis_title=None,
        legend_orientation="h",
        legend_traceorder="reversed",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    fig.update_xaxes(gridcolor="grey")
    fig.update_yaxes(gridcolor="grey")
    return fig

#### Creation du graph -> evolution du deplacement à differentes profondeurs en fonction du temps
def create_graph_4(dfi, chantier, inclino, profondeur, title):

    ''' trace l'évolution du deplacement à differentes profondeur en
    fonction du temps'''

    df = dfi.copy().set_index("profondeur").T
    df["Max"] = df.max(axis=1)
    df["Min"] = df.min(axis=1)
    df["Tête"] = df[0.5]
    df[f"{profondeur}m"] = df[profondeur]
    df = df.reset_index().rename(columns={"index": "date"})
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    fig = px.line(
        df,
        y=["Tête", "Min", "Max", f"{profondeur}m"],
        x="date",
        title=f"Evolution du déplacement {title} (mm)",
    )
    fig.update_yaxes(range=[-10, 25])
    fig.update_traces(hovertemplate=None)
    fig.update_layout(
        height=400,
        legend_title_text=None,
        yaxis_title="Déplacements (mm)",
        xaxis_title=None,
        legend_orientation="h",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 0, "t": 40, "l": 0, "b": 0},
    )
    fig.update_xaxes(gridcolor="grey")
    fig.update_yaxes(gridcolor="grey")
    return fig

#### Creation du graph -> N dernieres deplacements 3D (normal, tangent, profondeur)
def create_3d_graph(dfnormi, dftani, chantier, inclino, nb_courbes):

    ''' trace les n dernieres mesures de deplacments en 3D
    ('normal, tangent et profondeur)'''

    dfnorm, dftan = dfnormi.copy(), dftani.copy()
    profondeur = dfnorm.profondeur
    fig = go.Figure()
    for i in range(nb_courbes):
        normi = dfnorm.iloc[:, -1 - i]
        tani = dftan.iloc[:, -1 - i]
        fig.add_trace(
            go.Scatter3d(
                name=dfnorm.columns[-1 - i], x=normi, y=tani, z=profondeur, mode="lines"
            )
        )
    fig.update_layout(
        scene=dict(
            xaxis_title="Normal",
            yaxis_title="Tangent",
            zaxis_title="Profondeur",
            xaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
            ),
            yaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
            ),
            zaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
            ),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        legend_orientation="h",
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        height=400,
    )
    fig.update_scenes(zaxis_autorange="reversed")
    return fig
