import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd
from data import download_image, get_data
import numpy as np
from datetime import timedelta

user='Vallicorp'
mapbox_token = 'pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ'

colors = {
    'background': '#222222',
    'text': 'white'
}

coeff_Lamb_GPS = [[1.23952112e-05, 6.63800392e-07], [-4.81267332e-07,  8.98816386e-06]]
intercept_Lamb_GPS = [-20.17412175, 16.14120241]

def changement_repere(df, coef, intercept):
    lon = df.x * coef[0][0] + df.y * coef[0][1] + intercept[0]
    lat = df.x * coef[1][0] + df.y * coef[1][1] + intercept[1]
    df.x, df.y = lat, lon
    return df

def remove_xyz(string):
    return string.replace('.x','').replace('.y', '')

def first(col):
    i = 0
    for j in col:
        if not np.isnan(j) & (i == 0):
            i = j
            break
    return i

#######################  AFFICHAGE MAP GLOBALE   ######################################################

def affichage_map_geo():
    with engine.connect() as con:
        query1="select * from chantier_utilisateur where utilisateur ='%s'"%user
        liste_chantiers = pd.read_sql_query(query1, con=con).chantier.tolist()
        query2='SELECT * FROM chantier WHERE nom_chantier IN {}'.format(tuple(liste_chantiers))
        df = pd.read_sql_query(query2, con=con)

        fig = px.scatter_mapbox(
            df,
            lat="lat",
            lon="lon",
            hover_name="nom_chantier",
            hover_data={
                'lat':False,
                'lon':False,
            },
            color_discrete_sequence=["#FF8C00"],
            height=800,
            zoom=4
        )
        fig.update_layout(
            mapbox_style="dark",
            mapbox_accesstoken=mapbox_token
        )
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            margin=dict(l=0, r=0, t=10, b=0)
        )

    return fig


#######################  AFFICHAGE MAP CHANTIER   ######################################################

def affichage_map_chantier(data, chantier, mode,  preset = 1, affichage_plan = [1]):
    try:
        # with engine.connect() as con:
        #     query="select * from capteur where chantier ='%s'"%chantier
        #     df = pd.read_sql_query(query, con=con)

        df = pd.read_json(data['topo']).drop(columns=['date'])
        df = pd.DataFrame(df.apply(first)).T
        dfx = df[[col for col in df.columns if '.x' in col]].stack().reset_index().drop(columns=['level_0']).rename(columns={'level_1':'cible',0:'x'})
        dfy = df[[col for col in df.columns if '.y' in col]].stack().reset_index().drop(columns=['level_0']).rename(columns={'level_1':'cible',0:'y'})
        dfx.cible = dfx.cible.map(remove_xyz)
        dfy.cible = dfy.cible.map(remove_xyz)
        df2 = dfx.merge(dfy)
        df2 = changement_repere(df2, coeff_Lamb_GPS, intercept_Lamb_GPS)

        if mode == 1:
            fig = positions_GPS_capteur(df2)

        if mode ==  2:
            fig = positions_GPS_secteur(df2)

        if mode == 3:
            dff = pd.read_json(data['topo'])
            if preset==1 or preset==2:
                dff.date = pd.to_datetime(dff.date, format="%d/%m/%Y")
                last_date = dff.date.iloc[-1]
                dff = dff[dff.date > last_date - timedelta(30*preset)]

            fig = create_quiver(dff.drop(columns=["date"]).dropna(axis=1, how="all"), scale=750//preset)
            X = 2055229.22647546
            Y = 3179752.70410855
            x_size = 2055406.7254806 - 2055229.22647546
            y_size = 3179752.70410855 - 3179618.20410255
            fig.add_layout_image(
                dict(
                    source=download_image(chantier, 'plan.jpeg'),
                    xref="x",
                    yref="y",
                    x=X,
                    y=Y,
                    sizex=x_size,
                    sizey=y_size,
                    sizing="stretch",
                    layer="below",
                )
            )
            fig.update_xaxes(visible=False, range=[X, X + x_size])
            fig.update_yaxes(visible=False, range=[Y - y_size, Y])

        if affichage_plan==[1]:
            plan = download_image(chantier, 'plan.jpeg')
            layers = [
                dict(
                    below ='traces',
                    minzoom=16,
                    maxzoom=21,
                    opacity=0.7,
                    source = plan,
                    sourcetype= "image",
                    coordinates =  [
                        [7.4115104, 43.7321406],
                        [7.4137998, 43.7321406],
                        [7.4137998, 43.7310171],
                        [7.4115104, 43.7310171]
                    ],
                )
            ]
        else:
            layers = None

        mapbox = dict(
            zoom= 17.6,
            center=dict(
                lon=7.4126551,
                lat=43.7315788),
            layers=layers
        )

        fig.update_layout(
            mapbox=mapbox,
            clickmode='event+select',
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            margin=dict(l=20, r=20, t=10, b=0)
        )

        return fig
    except:
        return empty_figure()

#######################  CALCUL DES POSITIONS DES CAPTEURS  ######################################################

def positions_GPS_capteur(df):
    fig=go.Figure()
    fig.add_trace(go.Scattermapbox(
        name='cible',
        mode='markers+text',
        lat=df.x,
        lon=df.y,
        text=df.cible,
    ))

    fig.update_layout(
        mapbox_style="dark",
        mapbox_accesstoken=mapbox_token
    )
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        legend_title_text=None,
    )
    fig.update_traces(
        hovertemplate='%{text}',
        textfont_size=11)
    return fig

#######################  POSITIONNEMENT DES SECTEURS  ######################################################

def positions_GPS_secteur(df):
    df = changement_repere(df, coeff_Lamb_GPS, intercept_Lamb_GPS)
    df = df[(df.type=='cible') & (df.secteur != 'NON DEFINI')].groupby(['secteur']).mean().reset_index()

    fig = px.scatter_mapbox(
        df,
        lat="lat",
        lon="lon",
        color='secteur',
        text='secteur',
        hover_data={
            'lat':False,
            'lon':False,
            'secteur':False
        },
        )
    fig.update_layout(
        mapbox_style="dark",
        mapbox_accesstoken=mapbox_token,
        showlegend=False
    )
    fig.update_traces(marker=dict(size=50, opacity=0.6))
    return fig

def empty_figure():
    fig = go.Figure(
        layout=dict(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background']
            )
        )
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


#######################  CALCUL DES VECTEURS  ######################################################


def create_quiver(df, scale):
    first_indexes = df.apply(pd.Series.first_valid_index).to_dict()
    last_indexes = df.apply(pd.Series.last_valid_index).to_dict()
    first = [df.loc[first_indexes[col], col] for col in df.columns]
    last = [df.loc[last_indexes[col], col] for col in df.columns]
    first_x = [first[3 * i] for i in range(len(first) // 3)]
    first_y = [first[3 * i + 1] for i in range(len(first) // 3)]
    last_x = [last[3 * i] for i in range(len(last) // 3)]
    last_y = [last[3 * i + 1] for i in range(len(last) // 3)]
    u = [last_x[i] - first_x[i] for i in range(len(first_x))]
    v = [last_y[i] - first_y[i] for i in range(len(first_y))]
    while max(first_x) > 1.5 * np.mean(first_x):
        index = first_x.index(max(first_x))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    while max(first_y) > 1.5 * np.mean(first_y):
        index = first_y.index(max(first_y))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    while max(u) > 20 * mean_pos(u):
        index = u.index(max(u))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    while max(v) > 20 * mean_pos(v):
        index = v.index(max(v))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    while min(u) < 20 * mean_neg(u):
        index = u.index(min(u))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    while min(v) < 20 * mean_neg(v):
        index = v.index(min(v))
        first_x.pop(index)
        first_y.pop(index)
        u.pop(index)
        v.pop(index)
    return ff.create_quiver(first_x, first_y, u, v, scale=scale)


def mean_pos(list):
    return np.mean([i for i in list if i > 0])


def mean_neg(list):
    return np.mean([i for i in list if i < 0])

