import pandas as pd

from dash_express import Page


def get_df():
    return pd.DataFrame()

def create_ddu_page(app):
    page = Page(app,'/ddu','ДДУ', get_df, title='ДДУ', access_func=lambda: False, access_mode='view')
    return page
