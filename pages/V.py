import pandas as pd

from dash_express import Page


def get_df():
    return pd.read_csv('dash_express/titanic.csv')

def create_v_page(app):
    page = Page(app,'/vtorichka', 'Вторичка', title='Вторичка', access_func=lambda: False, access_mode='view')
    return page