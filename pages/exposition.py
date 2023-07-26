import pandas as pd

from dash_express import Page


def get_df():
    return pd.DataFrame()

def create_expos_page(app):
    page = Page(app,'/exposition','Экспозиция', title='Экспозиция', access_func=lambda: False, access_mode='view')
    return page
