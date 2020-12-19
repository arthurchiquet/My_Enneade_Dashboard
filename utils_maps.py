from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
from config import engine
import pandas as pd

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
                'lon':False
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

def affichage_map_chantier(chantier):
    try:
        with engine.connect() as con:
            query="select * from capteur where chantier ='%s' and type=1"%chantier
            coord_lambert = pd.read_sql_query(query, con=con)
        fig = px.scatter(
            coord_lambert,
            x="lat",
            y="lon",
            hover_name="capteur",
            template='plotly_dark',
            color_discrete_sequence=["#FF8C00"],
            width = 800,
            height=650,
            hover_data={
                    'lat':False,
                    'lon':False,
                    'secteur':False
                },
        )
        X = 2055229.22647546
        Y = 3179752.70410855
        x_size = 2055406.7254806 - 2055229.22647546
        y_size = 3179752.70410855 - 3179618.20410255

        fig.add_layout_image(
            dict(
                source=Image.open(f"data/{chantier}_plan_black.jpeg"),
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
        fig = go.Figure(
            layout=dict(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background']
                )
            )
        fig.update_xaxes(visible=False)
        fig.update_yaxes(visible=False)
        return fig
