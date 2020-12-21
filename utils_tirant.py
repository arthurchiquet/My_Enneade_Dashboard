import pandas as pd
import numpy as np
import plotly.express as px

def first(col):
    i = 0
    for j in col:
        if (not np.isnan(j)) & (i == 0):
            i = j
            break
    return i

def tension_blocage(df):
    df1 = df.copy()
    for col in df1.columns:
        df1[col] = df1[col] / first(df1[col])
    return df1


def format_df(df, list_tirants):
    df.date = pd.to_datetime(df.date, format="%d/%m/%Y")
    df = df.set_index("date")[list_tirants]
    df_ratio = tension_blocage(df)
    return df, df_ratio


def graph_tirant(df, list_tirants):
    df, df_ratio = format_df(df, list_tirants)
    fig1 = px.line(df.reset_index(), x='date', y=list_tirants, template="plotly_white")
    fig2 = px.line(df_ratio.reset_index(), x='date', y=list_tirants, template="plotly_white")
    fig1.update_layout(height=450, legend_title_text=None, yaxis_title="Tension (kN)", xaxis_title=None)
    fig2.update_layout(height=450, legend_title_text=None, yaxis_title="Tension (%)", xaxis_title=None)
    return fig1, fig2
