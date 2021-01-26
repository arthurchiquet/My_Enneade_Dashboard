import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd
from data import download_image, get_data
import numpy as np
from datetime import timedelta

mapbox_token = 'pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ'

colors = {
    'background': '#222222',
    'text': 'white'
}

coeff_Lamb_GPS = [[1.23952112e-05, 6.63800392e-07], [-4.81267332e-07,  8.98816386e-06]]
intercept_Lamb_GPS = [-20.17412175, 16.14120241]


def empty_figure():
    fig = {
        'data': [],
        'layout': {
        'plot_bgcolor': colors['background'],
        'paper_bgcolor': colors['background'],
        'font': {
            'color': colors['text']}
        }
    }
    return fig


def changement_repere(df, coef, intercept):
    lon = df.lat * coef[0][0] + df.lon * coef[0][1] + intercept[0]
    lat = df.lat * coef[1][0] + df.lon * coef[1][1] + intercept[1]
    df.lat, df.lon = lat, lon
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

def extract_position(df):
    df = df.drop(columns=['date'])
    df = pd.DataFrame(df.apply(first)).T
    dfx = df[[col for col in df.columns if '.x' in col]].stack().reset_index().drop(columns=['level_0']).rename(columns={'level_1':'cible',0:'lat'})
    dfy = df[[col for col in df.columns if '.y' in col]].stack().reset_index().drop(columns=['level_0']).rename(columns={'level_1':'cible',0:'lon'})
    dfx.cible = dfx.cible.map(remove_xyz)
    dfy.cible = dfy.cible.map(remove_xyz)
    df2 = dfx.merge(dfy)
    df2 = changement_repere(df2, coeff_Lamb_GPS, intercept_Lamb_GPS)
    return df2

#######################  AFFICHAGE MAP CHANTIER   ######################################################

def update_map_chantier(chantier, params):
    try:
        secteurs = params['secteur']
        del params['secteur']
    except:
        secteurs = []

    df = pd.concat({k: pd.DataFrame.from_dict(v, 'index') for k, v in params.items()},axis=0).reset_index().rename(columns={'level_0':'type','level_1':'capteur'})

    fig = px.scatter_mapbox(
        df,
        lat='lat',
        lon='lon',
        color='type',
        text='capteur',
        hover_data={'type':True}
    )

    fig.update_traces(
        hovertemplate='%{text}',
        textfont_size=11)

    # fig.update_traces(marker=dict(color='#DCDCDC'), selector=dict(name="cible"))
    fig.update_traces(marker=dict(size=20, color='#FF6347'), selector=dict(name="inclino"))
    fig.update_traces(marker=dict(size=20, color='#FF8C00'),selector=dict(name="tirant"))
    fig.update_traces(marker=dict(size=20, color='#7CFC00'),selector=dict(name="piezo"))
    fig.update_traces(marker=dict(size=20, color='#9370DB'),selector=dict(name="button"))


    # fig.for_each_trace(
    #     lambda trace: trace.update(marker=dict(size=20)) if trace.name == "inclino" else (),
    # )

    for secteur in secteurs:
        coords=secteurs[secteur]
        fig.add_trace(go.Scattermapbox(
            name=secteur,
            mode='lines',
            text=secteur,
            lon = [coords[0][0], coords[0][0], coords[1][0], coords[1][0], coords[0][0]],
            lat = [coords[1][1], coords[0][1], coords[0][1], coords[1][1], coords[1][1]],
            )
        )
        fig.update_traces(hovertemplate='Secteur', selector={'name':secteur})

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
            ]
        )
    ]
    mapbox = dict(
        zoom= 17.6,
        center=dict(
            lon=7.4126551,
            lat=43.7315788),
    )

    fig.update_layout(
        mapbox=mapbox,
        mapbox_style="dark",
        mapbox_accesstoken=mapbox_token,
        clickmode='event+select',
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin=dict(l=20, r=20, t=0, b=0),
        height=600,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        legend_title_text=None,
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                pad={"r": 10, "t": 10},
                showactive=False,
                x=0,
                xanchor="left",
                y=1.1,
                yanchor="top",
                buttons=list([
                    dict(label="Capteurs",
                         method="update",
                         args=[{"visible": [True for i in range(df.type.nunique())]+[False for i in range(len(secteurs))]}]),
                    dict(label="Secteurs",
                         method="update",
                         args=[{"visible": [False for i in range(df.type.nunique())]+[True for i in range(len(secteurs))]}]),
                    dict(label="Tous",
                         method="update",
                         args=[{"visible": [True for i in range(df.type.nunique())]+[True for i in range(len(secteurs))]}]),
                ]),
            ),
            dict(
                type="buttons",
                direction="left",
                pad={"l": 10, "t": 10},
                showactive=False,
                x=1,
                xanchor="right",
                y=1.1,
                yanchor="top",
                buttons=list([
                    dict(label='Afficher plan',
                         method='relayout',
                         args=[{'mapbox.layers' : layers}]),
                    dict(label='Masquer plan',
                         method='relayout',
                         args=[{'mapbox.layers' : None}]),
                    ]
                )
            )
        ]
    )

    return fig
    # except:
    #     return fig


#######################  CALCUL DES VECTEURS  ######################################################




# if mode == 3:
#             dff = pd.read_json(data['topo'])
#             if preset==1 or preset==2:
#                 dff.date = pd.to_datetime(dff.date, format="%d/%m/%Y")
#                 last_date = dff.date.iloc[-1]
#                 dff = dff[dff.date > last_date - timedelta(30*preset)]

# fig = create_quiver(dff.drop(columns=["date"]).dropna(axis=1, how="all"), scale=750//preset)
#             X = 2055229.22647546
#             Y = 3179752.70410855
#             x_size = 2055406.7254806 - 2055229.22647546
#             y_size = 3179752.70410855 - 3179618.20410255
#             fig.add_layout_image(
#                 dict(
#                     source=download_image(chantier, 'plan.jpeg'),
#                     xref="x",
#                     yref="y",
#                     x=X,
#                     y=Y,
#                     sizex=x_size,
#                     sizey=y_size,
#                     sizing="stretch",
#                     layer="below",
#                 )
#             )
#             fig.update_xaxes(visible=False, range=[X, X + x_size])
#             fig.update_yaxes(visible=False, range=[Y - y_size, Y])

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

