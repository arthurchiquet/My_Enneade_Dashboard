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
from utils_maps import empty_figure
from math import radians, cos, sin
from data import memoized_data
from scipy.stats import zscore
import json

colors = {"background": "#222222", "text": "white"}

layout = html.Div(
    [
        dcc.Graph(id="vector-plot", figure=empty_figure()),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                dbc.Row(
                    html.H4("Positions des cibles sélectionnées"), justify="center"
                ),
                dbc.Row(
                    dcc.Graph(id="3d-positions", figure=empty_figure()), justify='center'
                ),
            ], width=5),
            dbc.Col([
                dbc.Row(
                    html.H4("Déplacement normal, tangentiel et vertical (mm)"), justify="center"
                ),
                dbc.Row(
                    dcc.Graph(id="time-series", figure=empty_figure()), justify='center'
                ),
                ], width=7)
            ]
        )
    ]
)

@app.callback(
    Output("vector-plot", "figure"),
    Input("chantier-select", "data"),
    State('secteur-select', 'data'),
    State("global-params", "data"),
)
def update_graph_vector(chantier, secteur_selected, params):
    df = memoized_data(chantier, "actif", "topographie.csv")
    secteurs_params = params["secteur"]
    secteur = list(secteur_selected.keys())[0]
    coords = secteurs_params[secteur]
    return graph_vectors(df, coords, secteur)


@app.callback(
    Output("3d-positions", "figure"),
    Output("time-series", "figure"),
    Input('3d-positions', 'slectedData'),
    State("secteur-select", "data"),
    State("chantier-select", "data"),
    State("3d-positions", "figure"),
    State("time-series", "figure"),
)
def update_graphs(slectedData, secteur_selected, chantier, fig1, fig2):
    secteur = list(secteur_selected.keys())[0]
    list_capteur = secteur_selected[secteur]["cible"]
    df = memoized_data(chantier, "actif", "topographie.csv")
    df1 = extract_3d_positions(df, list_capteur, secteur)
    df2 = format_df(df, list_capteur, 0)
    return graph_3d_positions(df1, secteur), graph_topo(df2)
        # except:
        #     return empty_figure(), empty_figure(), empty_figure()
    # else:
    #     try:
    #         capteur=hoverData['points'][0]['customdata'][0]
    #         fig2=go.Figure(fig2)
    #         fig2.update_traces(
    #             line=dict(width=2, color='rgba(127, 255, 212, 0.3)')
    #         )
    #         fig2.update_traces(
    #             line=dict(width=4, color='#FF1493'), selector=dict(name=capteur)
    #         )
    #     except:
    #         pass
    #     return fig1, fig2, fig3


def affect(nom_capteur, liste_capteur, nom_secteur):
    if nom_capteur in liste_capteur:
        return nom_secteur
    else:
        return 'Hors secteur'

def extract_3d_positions(df, liste_capteur, secteur):
    df=df.drop(columns=["date"]).dropna(axis=1, how="all")
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    positions = {col : [df.loc[first_indexes[col], col]] for col in df.columns}
    df =pd.DataFrame.from_dict(positions).T
    df_x=df.iloc[[3*i for i in range(df.shape[0]//3)],:]
    df_y=df.iloc[[3*i+1 for i in range(df.shape[0]//3)],:]
    df_z=df.iloc[[3*i+2 for i in range(df.shape[0]//3)],:]
    df_x=df_x.reset_index().rename(columns={'index':'cible',0:'x'})
    df_y=df_y.reset_index().rename(columns={'index':'cible',0:'y'})
    df_z=df_z.reset_index().rename(columns={'index':'cible',0:'z'})
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
    df['secteur'] = df.apply(lambda x: affect(x['cible'], liste_capteur, secteur), axis=1)
    return df

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
            aspectratio=dict(x=2, y=2, z=1)
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

coefx= [80445.63079343, -5941.61901515]
interceptx = 1718838.64187916
coefy= [  4307.97154979, 110939.10161203]
intercepty = -1703790.12645452

def changement_repere(secteur, coefx, coefy, interceptx, intercepty):
    x1= secteur[0][0] * coefx[0] + secteur[0][1] * coefx[1] + interceptx
    x2= secteur[1][0] * coefx[0] + secteur[1][1] * coefx[1] + interceptx
    y1= secteur[1][0] * coefy[0] + secteur[1][1] * coefy[1] + intercepty
    y2= secteur[0][0] * coefy[0] + secteur[0][1] * coefy[1] + intercepty
    return x1, x2, y1, y2


def graph_vectors(df, secteur, nom_secteur):
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

    fig = go.Figure(go.Cone(
        x=df.x.tolist(),
        y=df.y.tolist(),
        z=df.z.tolist(),
        u=df.u.tolist(),
        v=df.v.tolist(),
        w=df.w.tolist(),
        colorscale='pinkyl',
        sizemode="absolute",
        text=df.cible,
        sizeref=350,
        name='cible'
        )
    )

    x1, x2, y1, y2 = changement_repere(secteur, coefx, coefy, interceptx, intercepty)
    z1 = df.z.min()
    z2 = df.z.max()

    fig.add_trace(
         go.Mesh3d(
            x=[x1, x1, x2, x2, x1, x1, x2, x2],
            y=[y1, y2, y2, y1, y1, y2, y2, y1],
            z=[z1, z1, z1, z1, z2, z2, z2, z2],

            i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.3,
            color='#FF1493',
            name=f'secteur {nom_secteur}'
        )
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
            aspectratio=dict(x=2, y=2, z=1)
        ),
        margin=dict(l=0, r=00, t=0, b=0),
        showlegend=False,
        plot_bgcolor=colors["background"],
        paper_bgcolor=colors["background"],
        font_color=colors["text"])
    return fig




