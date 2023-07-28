
## KPI cards
KPI cards are a basic part of monitoring business performance and tracking up-to-date information. Any card consists of a constant part (Container) and a variable part (KPI indicator)

The KPI rendering system is based on the use of the KPI class, which contains a container representation and the logic for calculating the indicator. The simplest implementation of KPI, with automatic generation of the calculation function, is presented in the FastKPI class:


```python
dmc.SimpleGrid(
    [
        app.add_kpi(FastKPI('survived', agg_func=func, h=150) for func in [np.mean, np.sum, np.max, np.min]
    ],
    cols=4
    )
```
FastKPI Initialization Parameters:

```
col = DataFrame Column
agg_func = pivot func for calculate kpi
pretty_func = pretty func for result calculate, for example: lambda x: f'{x:.1%}'
title = title of cards? default automatic generation
```

An advanced way to add KPI is to create your own card by inheriting from the base class of KPI:

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
The Plotly graphing library has more than 50 chart types to choose from. For Dash Express to work, you need to answer 2 questions:

1. Where is the graph located
2. How to build a graph

The answer to the first question is laid when developing the layout, by calling the page.add_graph(...) method in the location of the graph, a simple example:

```python
dmc.SimpleGrid(
    [
        page.add_graph(h='100%',render_func=bar_func),
        page.add_graph(h='100%',render_func=line_func),
    ],
    cols=2
    )
```

Through .add_graph is a function containing the logic of plotting to which the Dash Express application will pass the filtered DataFrame.
```python
def bar_func(df):
    return px.bar(df, x="nation", y="count", color="medal", title="Long-Form Input")
```

!!! Danger
    Render_func should return Plotly Figure, implementations from other libraries are not supported!



## Leaflet maps

If you use GeoPandas, you can add maps to your dashboard, it's as simple as adding a graph.:

```python
dmc.SimpleGrid(
    [
        page.add_map(geojson_func=None),
    ],
    cols=1
    )
```

geojson_func - should return GeoDataFrame.__get_interface__, if you do not need any additional transformations, do not specify this parameter, DashExpress will do everything for you.

```python
def geojson_func(gdf):
    gdf = gdf[gdf.geometry.geom_type == 'Polygon']
    return gdf.__geo_interface__
```

