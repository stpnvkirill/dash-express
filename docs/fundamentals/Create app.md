## Создание приложения

Первым шагом необходимо импортировать нужные библиотеки

```python
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

from hyper_dash import HyperDash, Page
```

Далее нужно инициализировать экземпляр приложения DashExpress.

```python
app = DashExpress()
```

Объект DashExpress реализует приложение Dash с предварительно настроенным интерфейсом и автоматической генерацией обратных вызовов для быстрого создания интерактивных многостраничных приложений веб-аналитики.

## Определение страницы

Каждая страница приложения - отдельный объект, экземпляр класса `dash_express.Page`. Страница содержит в себе исходные данные для анализа, функции создания графиков и список фильтров.

```python
page = Page(
    app=app,                    # Приложение HyperDash
    url_path='/',               # url страницы
    name='Обзор',               # Название страницы в кнопках навигации
    getdf=get_df,               # Функция получения pd.DataFrame
    title='Обзор',              # title страницы
    )
```

## Получение данных

Функция `get_df` содержит в себе логику получения данных: 

```python
get_df = lambda: pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
```

## Макет дашборда

Далее необходимо определить макет дашборда. рекомендуем использовать dmc.Grid и dmc.SimpleGrid

```python
# Dashboard layout
page.layout = dmc.SimpleGrid(
    page.add_graph(h='100%',render_func=bar_func)
    )
```

Параметр render_func метода page.add_graph - это функция генерации графика по данным из DataFrame

```python
# The logic of drawing a graph
bar_func = lambda df: px.histogram(df, x='continent', y='lifeExp', histfunc='avg')
```

Последним действием остается добавление фильтров, которое делается простым выховом метода page.add_filter и указанием столбца фильтрации.

```python
page.add_autofilter('continent', multi=True)
page.add_autofilter('country', multi=True)
page.add_autofilter('lifeExp', multi=True)
```

Страница готова, теперь нужно инициализировать ее в DashExpress:

```python
app.regester_page(page)
```
## Запуск приложения

Этих действий достаточно для создания полнофункционального дашборда, поэтому можно запускать приложение.


```python
app.run()
```

## Полный код минимального приложения

```python
import pandas as pd
import plotly.express as px
import dash_mantine_components as dmc

from hyper_dash import HyperDash, Page


# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = HyperDash()

# Initialize the Page
page = Page(
    app=app,                    # Приложение HyperDash
    url_path='/',               # url страницы
    name='Обзор',               # Название страницы в кнопках навигации
    getdf=lambda:df,            # Функция получения pd.DataFrame
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
app.run()

```