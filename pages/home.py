import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dash_express import Page, dmc, html, Patch, FastKPI
import numpy as np


PRIMARY_COL_HEIGHT = 'calc((100vh - 140px)*0.8 - 165px)'
SECONDARY_COL_HEIGHT = 'calc((100vh - 140px)*0.8/2 - 166px)'
CARD_COL_HEIGHT = 'calc((100vh - 140px)*0.8/4)'

PRIMARY_COL_HEIGHT_MIN = 100# 800 *0.8 - 15
SECONDARY_COL_HEIGHT_MIN = 100#800 *0.8/2 - 16
CARD_COL_HEIGHT_MIN = 100#800 *0.8/4
skeleton_kwargs = {}


def bar_who(df):
    index, values, color = 'who','survived', 'alone'
    pv = pd.pivot_table(df, index=[index, color] if color else index, values=[values], 
                        aggfunc=len).reset_index()

    x = pv[index].unique()
    fig = go.Figure()
    for c in pv[color].unique():
        fig.add_trace(go.Bar(x=x, y=pv[pv[color] == c][values],
                            base= 0 if  not c else pv[pv[color] == c][values] * -1,
                            marker_color='lightslategrey' if not c else 'crimson',
                        name='die' if c else 'live',)
                        )

        
    fig.update_traces(opacity=0.6,)
    fig.update_layout(
        title=dict(text="GDP-per-capita"),
    )
    return fig

def bar_class(df): 
    index, values, color = 'class','survived', 'alone'

    pv = pd.pivot_table(df, index=[index, color] if color else index, values=values, aggfunc=len).reset_index()

    x = pv[index].unique()

    fig = go.Figure()
    for c in pv[color].unique():
        fig.add_trace(go.Bar(x=x, y=pv[pv[color] == c][values],
                            base= 0 if  not c else pv[pv[color] == c][values] * -1,
                            marker_color='lightslategrey' if not c else 'crimson',
                        name='die' if c else 'live'))
    fig.update_traces(opacity=0.6)
    fig.update_layout(
        title=dict(text="GDP-per-capita")
    )
    return fig
    
def get_df():
    return pd.read_csv('dash_express/titanic.csv')

def get_layout(app):    
    return html.Div(
        [
            dmc.SimpleGrid(
                cols=4,
                spacing="md",
                breakpoints=[{'maxWidth': 'sm', 'cols': 2}],
                children=[app.add_kpi(FastKPI('survived', h=CARD_COL_HEIGHT, mih=CARD_COL_HEIGHT_MIN))] + 
                [dmc.Skeleton(h=CARD_COL_HEIGHT, mih=CARD_COL_HEIGHT_MIN, **skeleton_kwargs) for i in range(3)]
            ),
            dmc.SimpleGrid(
                pt=15,
                cols=2,
                spacing="md",
                breakpoints=[{'maxWidth': 'sm', 'cols': 1}],
                children=[
                        app.add_graph(h=PRIMARY_COL_HEIGHT, mih=PRIMARY_COL_HEIGHT_MIN, render_func=bar_who),
                        app.add_graph(h=PRIMARY_COL_HEIGHT, mih=PRIMARY_COL_HEIGHT_MIN, render_func=bar_class),
                ]
            ),
            dmc.SimpleGrid(
                pt=15,
                cols=2,
                spacing="md",
                breakpoints=[{'maxWidth': 'sm', 'cols': 1}],
                children=[
                        app.add_graph(h=PRIMARY_COL_HEIGHT, mih=PRIMARY_COL_HEIGHT_MIN, render_func=bar_who),
                        app.add_graph(h=PRIMARY_COL_HEIGHT, mih=PRIMARY_COL_HEIGHT_MIN, render_func=bar_class),
                ]
            ),
        ])

def create_home_page(app):
    page = Page(app,'/','Обзор',get_df, 'Обзор')
    page.layout = get_layout(page)
    # page.add_autofilter('continent', multi=True, clearable=True, searchable=True,)
    page.add_autofilter('who', multi=True)
    page.add_autofilter('age', multi=True)
    # page.add_autofilter('date', multi=True)
    return page
