import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd
from data import download_image

user='Vallicorp'
mapbox_token = 'pk.eyJ1IjoiYXJ0aHVyY2hpcXVldCIsImEiOiJja2E1bDc3cjYwMTh5M2V0ZzdvbmF5NXB5In0.ETylJ3ztuDA-S3tQmNGpPQ'

colors = {
    'background': '#222222',
    'text': '#FF8C00'
}



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
            height=550,
            zoom=4)
        fig.update_layout(mapbox_style="dark", mapbox_accesstoken=mapbox_token)
        fig.update_layout(
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font_color=colors['text'],
            margin=dict(l=100, r=100, t=20, b=15)
        )
    return fig

def affichage_map_chantier(chantier, mode):
    try:
        plan = download_image(chantier, 'plan.jpeg')
        with engine.connect() as con:
            query="select * from capteur where chantier ='%s'"%chantier
            df = pd.read_sql_query(query, con=con)

        if mode == 'GPS':
            fig = positions_GPS_capteur(df)

        if mode ==  'secteurs':
            fig = positions_GPS_secteur(df)

        if mode == 'vecteurs':
            fig = create_quiver(df)

        X = 2055229.22647546
        Y = 3179752.70410855
        x_size = 2055406.7254806 - 2055229.22647546
        y_size = 3179752.70410855 - 3179618.20410255

        fig.add_layout_image(
            dict(
                source=plan,
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

        fig.update_layout(
                # title={
                #     'text': chantier,
                #     'xanchor': 'center',
                #     'yanchor': 'top',
                #     'x':0.5,
                #     },
                title_font_color="#FF8C00",
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                margin={"r":30,"t":10,"l":30,"b":20}
            )

        fig.update_xaxes(
            range=[X, X + x_size],
            linecolor='white',
            linewidth=2,
            mirror=True,
            showticklabels=False,
            title=None,
            showgrid=False)

        fig.update_yaxes(
            range=[Y - y_size, Y],
            linecolor='white',
            linewidth=2,
            mirror=True,
            showticklabels=False,
            title=None,
            showgrid=False)
        return fig
    except:
        return empty_figure()


def positions_GPS_capteur(df):
    fig = px.scatter(
        df,
        x="lat",
        y="lon",
        hover_name="capteur",
        template='plotly_dark',
        # color_discrete_sequence=["#FF8C00"],
        color='type',
        height=550,
        # hover_data={
        #         'type':True
        #     },
    )
    fig.update_traces(hovertemplate = " %{color} : %{hover_name}")
    return fig

def positions_GPS_secteur(df):
    df = df[df.type=='cible'].groupby(['secteur']).mean().reset_index()

    fig = px.scatter(
        df,
        x="lat",
        y="lon",
        template='plotly_dark',
        text="secteur",
        color='secteur',
        height=550,
        hover_name='secteur',
        hover_data={
            'lat':False,
            'lon':False,
            'secteur':False
        },
        )
    fig.update_layout(showlegend=False)
    fig.update_traces(marker=dict(size=50,line=dict(width=2)))
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


def create_quiver(df):
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
    return ff.create_quiver(first_x, first_y, u, v, scale=250)


def mean_pos(list):
    return np.mean([i for i in list if i > 0])


def mean_neg(list):
    return np.mean([i for i in list if i < 0])

