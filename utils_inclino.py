import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from data import get_data

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
