import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

from dash_express import DashExpress, Page

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Incorporate data
def get_df():
    # print('!')
    return df

# Initialize the app
app = DashExpress()

# Initialize the Page
page = Page(
    app=app,                    # Приложение HyperDash
    url_path='/',               # url страницы
    name='Обзор',               # Название страницы в кнопках навигации
    get_df=get_df,            # Функция получения pd.DataFrame
    title='Обзор',              # title страницы
    )

# The logic of drawing a graph
bar_func = lambda df: px.histogram(df, x='continent', y='lifeExp', histfunc='avg')

# Dashboard layout
page.layout = dmc.SimpleGrid(
    page.add_graph(h='100%',render_func=bar_func)
    )

# By which columns to filter
page.add_autofilter('continent', multi=True)
page.add_autofilter('country', multi=True)
page.add_autofilter('lifeExp', multi=True)

app.regester_page(page)
app.run(debug=True)