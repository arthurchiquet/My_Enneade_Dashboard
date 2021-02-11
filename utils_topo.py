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
        dcc.Graph(id="graph-3D", figure=empty_figure()),
        html.Hr(),
        html.Br(),
        dbc.Row(html.H4('Dépalcement des cibles X, Y, et Z (mm)'), justify='center'),
            dcc.Graph(id="time-series", figure=empty_figure())
    ]
)

@app.callback(
    Output("graph-3D", "figure"),
    Input("chantier-select", "data"),
    State('secteur-select', 'data'),
    State("global-params", "data"),
)
def update_graph_vector(chantier, secteur_selected, params):
    if secteur_selected == {}:
        return empty_figure()
    else:
        df = memoized_data(chantier, "actif", "topographie.csv")
        secteurs_params = params["secteur"]
        secteur = list(secteur_selected.keys())[0]
        list_capteur = secteur_selected[secteur]["cible"]
        coords = secteurs_params[secteur]
        df1 = extract_3d_positions(df, list_capteur, secteur)
        df2 = format_df_vector(df)
        return graph_3D(df1, df2, coords, secteur)


@app.callback(
    Output("time-series", "figure"),
    Input("secteur-select", "data"),
    State("chantier-select", "data"),
)
def update_time_serie(secteur_selected, chantier):
    if secteur_selected == {}:
        return empty_figure()
    else:
        secteur = list(secteur_selected.keys())[0]
        df = memoized_data(chantier, "actif", "topographie.csv")
        list_capteur = secteur_selected[secteur]["cible"]
        df = format_df(df, list_capteur, 0)
        fig = graph_topo(df, height=700)
        return fig

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


def graph_3D(df1, df2, secteur, nom_secteur):

    fig = go.Figure(
        data=[go.Scatter3d(
            x=df1.x,
            y=df1.y,
            z=df1.z,
            customdata=df1[['cible','secteur']],
            name='Position',
            text = df1.cible,
            mode='markers',)
        ]
    )
    fig.update_traces(
        marker=dict(size=3, opacity=0.6, color='#7FFFD4')
    )
    fig.add_trace(go.Cone(
        x=df2.x.tolist(),
        y=df2.y.tolist(),
        z=df2.z.tolist(),
        u=df2.u.tolist(),
        v=df2.v.tolist(),
        w=df2.w.tolist(),
        colorscale='pinkyl',
        sizemode="absolute",
        text=df2.cible,
        name='Déplacement',
        sizeref=350,
        )
    )

    x1, x2, y1, y2 = changement_repere(secteur, coefx, coefy, interceptx, intercepty)
    z1 = df1[df1.secteur == nom_secteur].z.min()-4
    z2 = df1[df1.secteur == nom_secteur].z.max()+4

    fig.add_trace(
         go.Mesh3d(
            x=[x1, x1, x2, x2, x1, x1, x2, x2],
            y=[y1, y2, y2, y1, y1, y2, y2, y1],
            z=[z1, z1, z1, z1, z2, z2, z2, z2],

            i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            opacity=0.15,
            color='#FF1493',
            name=f'secteur {nom_secteur}'
        )
    )

    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="left",
                pad={"r": 10, "t": 0},
                showactive=False,
                x=0.45,
                xanchor="left",
                y=1.15,
                yanchor="top",
                buttons=list(
                    [
                        dict(
                            label="Tous",
                            method="update",
                            args=[
                                {
                                    "visible": [True, True, True]
                                }
                            ],
                        ),
                        dict(
                            label="Positions",
                            method="update",
                            args=[
                                {
                                    "visible": [True, False, False]
                                }
                            ],
                        ),
                        dict(
                            label="Vecteurs",
                            method="update",
                            args=[
                                {
                                    "visible": [False, True, False]
                                }
                            ],
                        ),
                        dict(
                            label="Positions + Secteur",
                            method="update",
                            args=[
                                {
                                    "visible": [True, False, True]
                                }
                            ],
                        ),
                        dict(
                            label="Vecteurs + Secteur",
                            method="update",
                            args=[
                                {
                                    "visible": [False, True, True]
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
            camera=dict(eye=dict(x=0,y=-0.3,z=1.25))
        ),
        margin=dict(l=0, r=0, t=0, b=0),
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

def format_df_vector(df):
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
    return df[filtered_entries].reset_index()




