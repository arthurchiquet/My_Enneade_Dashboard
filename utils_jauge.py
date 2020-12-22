import pandas as pd
import numpy as np
import plotly.express as px
from data import get_data

colors = {
    'background': '#222222',
    'text': 'white'
}

def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i

def diff_jauge(df):
    for col in df.columns:
        df[col] = df[col] / first(df[col])
    return df

def format_df(df):
    df.Date = pd.to_datetime(df.Date, format="%d/%m/%Y")
    df = df.set_index("Date")
    df = diff_jauge(df)
    return df

def graph_jauge(chantier, jauge):
    df = format_df(get_data(chantier, 'actif', 'jauges.csv', sep=False)[['Date',jauge]])
    fig = px.line(df.reset_index(), x="Date", y=df.columns, line_shape='spline')
    fig.update_layout(
        height=550,
        showlegend=False,
        yaxis_title="% Jauges",
        xaxis_title=None,
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    return fig
