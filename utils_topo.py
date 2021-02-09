import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from config import engine
import pandas as pd
import numpy as np
from server import app
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils_maps import empty_figure
from math import radians, cos, sin
from data import memoized_data
from scipy.stats import zscore
import json

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        html.Br(),
        dbc.Row([
            dbc.Col([
                dbc.Row(
                    html.H4("Positions des cibles sélectionnées"), justify="center"
                ),
                dbc.Row(
                    [dcc.Loading(dcc.Graph(id="3d-positions", figure=empty_figure()), type="graph")], justify='center'
                ),
            ], width=5),
            dbc.Col([
                dbc.Row(
                    html.H4("Déplacement normal, tangentiel et vertical (mm)"), justify="center"
                ),
                dbc.Container(
                    [dcc.Graph(id="time-series", figure=empty_figure())], fluid=True
                ),
                ], width=7)
            ]
        ),
        html.Br(),
        html.Hr(),
        html.Br(),
        dbc.Row(html.H4("Vecteurs de déplacements (mm)"), justify='center'),
        dbc.Container(dcc.Graph(id="vector-plot", figure=empty_figure()), fluid=True)
        # html.Pre(id='hover-data')
    ]
)

# @app.callback(
#     Output('hover-data', 'children'),
#     Input('3d-positions', 'figure'))
# def display_hover_data(hoverData):
#     return json.dumps(hoverData['data'], indent=2)


@app.callback(
    Output("3d-positions", "figure"),
    Input("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_3d_graph(secteur_selected, chantier):
    try:
        secteur = list(secteur_selected.keys())[0]
        list_capteur = secteur_selected[secteur]["cible"]
        df = memoized_data(chantier, "actif", "topographie.csv")
        df = extract_3d_positions(df, list_capteur, secteur)
        return graph_3d_positions(df, secteur)
    except:
        return empty_figure()


@app.callback(
    Output("time-series", "figure"),
    Input('3d-positions', 'hoverData'),
    State("secteur-select", "data"),
    State("chantier-select", "data"),
    State("time-series", "figure"),
)
def update_timeseries(hoverData, secteur_selected, chantier, fig):
    if fig==empty_figure():
        try:
            secteur = list(secteur_selected.keys())[0]
            list_capteur = secteur_selected[secteur]["cible"]
            df = memoized_data(chantier, "actif", "topographie.csv")
            df = format_df(df, list_capteur, 0)
            return graph_topo(df)
        except:
            return empty_figure()
    else:
        try:
            capteur=hoverData['points'][0]['customdata'][0]
            fig=go.Figure(fig)
            fig.update_traces(
                line=dict(width=2, color='rgba(127, 255, 212, 0.3)')
            )
            fig.update_traces(
                line=dict(width=4, color='#FF1493'), selector=dict(name=capteur)
            )
        except:
            pass
        return fig

@app.callback(
    Output("vector-plot", "figure"),
    Input("chantier-select", "data"),
)
def update_3d_graph(chantier):
    try:
        df = memoized_data(chantier, "actif", "topographie.csv")
        return graph_vectors(df)
    except:
        return empty_figure()


def affect(nom_capteur, liste_capteur, nom_secteur):
    if nom_capteur in liste_capteur:
        return nom_secteur
    else:
        return 'Hors secteur'

def extract_3d_positions(df, liste_capteur, secteur):
    df=df.rename(columns={'Date':'date'})
    df = df.drop(columns=["date"])
    df = pd.DataFrame(df.apply(first)).T
    dfx = (
        df[[col for col in df.columns if ".x" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "x"})
    )
    dfy = (
        df[[col for col in df.columns if ".y" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "y"})
    )
    dfz = (
        df[[col for col in df.columns if ".z" in col]]
        .stack()
        .reset_index()
        .drop(columns=["level_0"])
        .rename(columns={"level_1": "cible", 0: "z"})
    )
    dfx.cible = dfx.cible.map(remove_xyz)
    dfy.cible = dfy.cible.map(remove_xyz)
    dfz.cible = dfz.cible.map(remove_xyz)
    df2 = dfx.merge(dfy).merge(dfz)
    df2['secteur'] = df2.apply(lambda x: affect(x['cible'], liste_capteur, secteur), axis=1)
    df2 = df2[(df2.x < df2.x.mean()*1.2)&(df2.x > df2.x.mean()*0.8)&(df2.y < df2.y.mean()*1.2)&(df2.y >df2.y.mean()*0.8)&(df2.z < df2.z.mean()*1.2)&(df2.z >df2.z.mean()*0.8)]
    return df2

def graph_3d_positions(df, secteur):

    manu1 = list((df.cible.map(manu_auto_sd)=='manu') & (df.secteur==secteur))
    manu2 = list((df.cible.map(manu_auto_sd)=='manu') & (df.secteur!=secteur))
    auto1 = list((df.cible.map(manu_auto_sd)=='auto') & (df.secteur==secteur))
    auto2 = list((df.cible.map(manu_auto_sd)=='auto') & (df.secteur!=secteur))
    sd1 = list((df.cible.map(manu_auto_sd)=='sd') & (df.secteur==secteur))
    sd2 = list((df.cible.map(manu_auto_sd)=='sd') & (df.secteur!=secteur))

    df1=df[manu1]
    df2=df[manu2]
    df3=df[auto1]
    df4=df[auto2]
    df5=df[sd1]
    df6=df[sd2]

    fig = go.Figure(
        data=[go.Scatter3d(
            x=df1.x,
            y=df1.y,
            z=df1.z,
            customdata=df1[['cible','secteur']],
            mode='markers',
            name='Manuel_S')
        ]
    )

    fig.add_trace(
        go.Scatter3d(
            x=df2.x,
            y=df2.y,
            z=df2.z,
            customdata=df2[['cible','secteur']],
            mode='markers',
            name='Manuel_HS'
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=df3.x,
            y=df3.y,
            z=df3.z,
            customdata=df3[['cible','secteur']],
            mode='markers',
            name='Auto_S'
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=df4.x,
            y=df4.y,
            z=df4.z,
            customdata=df4[['cible','secteur']],
            mode='markers',
            name='Auto_HS'
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=df5.x,
            y=df5.y,
            z=df5.z,
            customdata=df5[['cible','secteur']],
            mode='markers',
            name='Sd_S'
        )
    )

    fig.add_trace(
        go.Scatter3d(
            x=df6.x,
            y=df6.y,
            z=df6.z,
            customdata=df6[['cible','secteur']],
            mode='markers',
            name='Sd_HS'
        )
    )

    fig.update_traces(
        marker=dict(size=3, opacity=0.6, color='#7FFFD4')
    )

    fig.update_traces(
        marker=dict(size=3, opacity=1, color='#FF1493'), selector=dict(name='Manuel_S')
    )

    fig.update_traces(
        marker=dict(size=3, opacity=1, color='#FF1493'), selector=dict(name='Auto_S')
    )

    fig.update_traces(
        marker=dict(size=3, opacity=1, color='#FF1493'), selector=dict(name='Sd_S')
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="right",
                pad={"r": 10, "t": 0},
                showactive=False,
                x=0.15,
                xanchor="left",
                y=1.08,
                yanchor="top",
                buttons=list(
                    [
                        dict(
                            label="Manuel",
                            method="update",
                            args=[
                                {
                                    "visible": [True, True, False, False, False, False]
                                }
                            ],
                        ),
                        dict(
                            label="Auto",
                            method="update",
                            args=[
                                {
                                    "visible": [False, False, True, True, False, False]
                                }
                            ],
                        ),
                        dict(
                            label="Sous-dalle",
                            method="update",
                            args=[
                                {
                                    "visible": [False, False, False, False, True, True]
                                }
                            ],
                        ),
                        dict(
                            label="Tous",
                            method="update",
                            args=[
                                {
                                    "visible": [True, True, True, True, True, True]
                                }
                            ],
                        ),
                    ]
                )
            ),
        ],
        scene=dict(
            xaxis_title="Est / Ouest",
            yaxis_title="Nord / Sud",
            zaxis_title="Z",
            xaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            yaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            zaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
        ),
        margin=dict(l=20, r=20, t=0, b=0),
        width=650,
        height=470,
        showlegend=False,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
    )
    return fig


def first(col):
    i = 0
    for j in col:
        if not np.isnan(j) & (i == 0):
            i = j
            break
    return i

def delta(df):
    for col in df.columns:
        df[col] = (df[col] - first(df[col])) * 1000
    return df

def get_columns(df):
    col = [i[:-2] for i in df.columns][1:]
    return [col[i] for i in range(0, df.shape[1] - 1, 3)]

def select_columns(df, liste):
    return [col for col in df.columns if col[:-2] in liste]

def facet_name_xyz(string):
    if "x" in string:
        return "x"
    elif "y" in string:
        return "y"
    elif "z" in string:
        return "z"

def facet_name_ntz(string):
    if "x" in string:
        return "Normal"
    elif "y" in string:
        return "Tangent"
    elif "z" in string:
        return "Vertical"

def remove_xyz(string):
    return string[:-2]

def manu_auto_sd(cible):
    if cible[:2].lower()=='sd':
        return 'sd'
    else:
        return cible[:4].lower()

def format_df(df, list_cibles, angle=0, repere='xyz'):
    df=df.rename(columns={'Date':'date'})
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    liste_colonnes = select_columns(df, list_cibles)
    df = df.set_index("date")[liste_colonnes]
    df = delta(df)
    for i in range(df.shape[1] // 3):
        norm = df.iloc[:, 3 * i] * cos(radians(angle)) - df.iloc[:, 3 * i + 1] * sin(
            radians(angle)
        )
        tang = df.iloc[:, 3 * i + 1] * cos(radians(angle)) + df.iloc[:, 3 * i] * sin(
            radians(angle)
        )
        df.iloc[:, 3 * i] = norm
        df.iloc[:, 3 * i + 1] = tang
    df = df.stack().reset_index()
    if repere=='xyz':
       df["Axe"] = df["level_1"].map(facet_name_xyz)
    else:
        df["Axe"] = df["level_1"].map(facet_name_ntz)
    df["cible"] = df["level_1"].map(remove_xyz)
    return df.rename(columns={0: "delta"}).drop(columns="level_1")


def graph_topo(df, height=470, memo=False, spacing=0.08, showlegend=True):
    fig = px.line(
        df,
        x="date",
        y="delta",
        facet_row="Axe",
        color="cible",
        hover_data={'cible' : True},
        facet_row_spacing=spacing,
    )
    fig.update_xaxes(showgrid=False, title=dict(text=None))
    fig.update_yaxes(mirror='all', title=dict(text=None), gridcolor="grey", nticks=15)
    fig.update_traces(hovertemplate=None, line=dict(color='rgba(127, 255, 212, 0.4)', width=2))
    fig.update_layout(
        showlegend=showlegend,
        height=height,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],
        margin={"r": 10, "t": 10, "l": 0, "b": 0},
    )
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    return fig


def graph_vectors(df):
    df=df.drop(columns=["date"]).dropna(axis=1, how="all")
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    last_indexes = df.apply(pd.Series.last_valid_index).to_dict()
    first_last = {col : [df.loc[first_indexes[col], col],df.loc[last_indexes[col], col]] for col in df.columns}
    df =pd.DataFrame.from_dict(first_last).T.rename(columns={0:'first',1:'last'})
    df['norm']=(df['last']-df['first'])
    df_x=df.iloc[[3*i for i in range(df.shape[0]//3)],:]
    df_y=df.iloc[[3*i+1 for i in range(df.shape[0]//3)],:]
    df_z=df.iloc[[3*i+2 for i in range(df.shape[0]//3)],:]
    df_x=df_x.reset_index().rename(columns={'index':'cible','first':'x','norm':'u'}).drop(columns=['last'])
    df_y=df_y.reset_index().rename(columns={'index':'cible','first':'y','norm':'v'}).drop(columns=['last'])
    df_z=df_z.reset_index().rename(columns={'index':'cible','first':'z','norm':'w'}).drop(columns=['last'])
    df_x.cible=df_x.cible.map(remove_xyz)
    df_y.cible=df_y.cible.map(remove_xyz)
    df_z.cible=df_z.cible.map(remove_xyz)
    df=df_x.merge(df_y).merge(df_z)
    df=df.set_index('cible')
    z_scores = zscore(df)
    abs_z_scores = np.abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    df= df[filtered_entries]
    df= df.reset_index()
    fig = go.Figure(data = go.Cone(
        x=df.x.tolist(),
        y=df.y.tolist(),
        z=df.z.tolist(),
        u=df.u.tolist(),
        v=df.v.tolist(),
        w=df.w.tolist(),
        colorscale='hsv',
        # opacity=0.7,
        sizemode="absolute",
        hovertext=df.cible,
        sizeref=500)
    )
    fig.update_layout(
         scene=dict(
            xaxis_title="Est / Ouest",
            yaxis_title="Nord / Sud",
            zaxis_title="Z",
            xaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            yaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
            zaxis=dict(
                backgroundcolor=colors["background"],
                gridcolor="grey",
                showbackground=False,
                showticklabels=False,
                showline=True,
                linewidth=2,
                linecolor='white',
                mirror=True
            ),
        ),
        margin=dict(l=0, r=00, t=0, b=0),
        # width=1000,
        # height=470,
        showlegend=False,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"],)
    return fig



