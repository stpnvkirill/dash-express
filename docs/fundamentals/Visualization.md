
## KPI cards
KPI карточки это базовая часть мониторинга эффективности бизнеса и отслеживание актуальной информации. Любая карточка состоит из постоянной части (Контейнера) и переменной части (KPI показателя)

Система рендера KPI  построена на использовании класса KPI, содержащего представление контейнера и логику расчета показателя. Простейшая реализация KPI, с автогенерацией расчетной функции представлена в классе FastKPI:


```python
dmc.SimpleGrid(
    [
        app.add_kpi(FastKPI('survived', agg_func=func, h=150) for func in [np.mean, np.sum, np.max, np.min]
    ],
    cols=4
    )
```
Параметры инициализации FastKPI:

```
col = DataFrame Column
agg_func = pivot func for calculate kpi
pretty_func = pretty func for result calculate, for example: lambda x: f'{x:.1%}'
title = title of cards? default automatic generation
```

Продвинутый вариант добавления KPI создание своей собственной карточки путем наследования от базового класса KPI:

```python
from dash_express import KPI

class MyKPI(KPI):
    def __init__(self, ...):
        ...

    def render_layout(self, id):
        '''Render Container'''
        return dmc.Card(...)

    def render_func(self,df):
        '''Compute & Render value'''
        return ...

app.add_kpi(MyKPI())

```



## Plotly Figure
The Plotly graphing library has more than 50 chart types to choose from. Для работы DashExpress требуется ответить на 2 вопроса:
 
1. Где график расположен
2. Как график построить

Ответ на первый вопрос закладывается при разработке макета, путем вызова метода page.add_graph(...) в месте нахождения графика, простой пример:

```python
dmc.SimpleGrid(
    [
        page.add_graph(h='100%',render_func=bar_func),
        page.add_graph(h='100%',render_func=line_func),
    ],
    cols=2
    )
```

Через .add_graph задается функция, содержащая логику построения графика в которую приложение DashExpress передаст отфильтрованный DataFrame.
```python
def bar_func(df):
    return px.bar(df, x="nation", y="count", color="medal", title="Long-Form Input")
```

!!! Danger
    Render_func должна возвращать Plotly Figure, реализации от других библиотек не поддерживаются! 



## Leaflet maps

Если вы используете GeoPandas, вы можете добавлять карты на вашу панель, сделать это так же просто, как и добавить график:

```python
dmc.SimpleGrid(
    [
        page.add_map(geojson_func=None),
    ],
    cols=1
    )
```

geojson_func - должная возвращать GeoDataFrame.__geo_interface__, если вам не нужны никакие дополнительные преобразования не указывайте данный параметр, DashExpress сделает все за вас.

```python
def geojson_func(gdf):
    gdf = gdf[gdf.geometry.geom_type == 'Polygon']
    return gdf.__geo_interface__
```

## Requirements

Python 3.7+

DashExpress stands on the shoulders of giants:

* <a href="https://dash.plotly.com/" class="external-link" target="_blank">Plotly Dash</a> for the web parts.
* <a href="https://pandas.pydata.org/" class="external-link" target="_blank">Pandas DataFrame</a> for the data store & compute measure.
* <a href="https://www.dash-mantine-components.com/" class="external-link" target="_blank">Dash Mantine Components</a> for the create pretty UI
* <a href="https://dash-leaflet.herokuapp.com/" class="external-link" target="_blank">Dash Leaflet</a> for the create maps

## License

This project is licensed under the terms of the MIT license.
