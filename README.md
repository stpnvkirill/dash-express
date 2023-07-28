# Fast analytical web application with DashExpress

[Documentation](https://stpnvkirill.github.io/dash-express/)

Build your next dashboard even faster with premade responsive UI and automatic callback-function. DashExpress is a wrapper over the Plotly Dash web framework, which allows you to simplify and speed up the creation of multi-page analytical applications based on data from pd.DataFrame.

```console
pip install dash-express
```

Currently supported: Charts, KPI, Geographical Maps

The key features are:

* **High Performance**: Provided by built-in optimization methods of Dash callback functions.
* **Fast to code**: Using a pre-configured UI and automatically generated callback functions.
* **Based on Pandas**: A library familiar to all analysts.
* **Used Mantine UI**: Pretty UI by Mantine React Library.
* **Include Dark Theme**: Use a dark theme for all components (including graphs and maps) without any additional actions.


## Minimal full-featured dashboard

![Image title](https://raw.githubusercontent.com/stpnvkirill/dash-express/main/docs/assets/gifs/min_app.gif)

The first step is to import the necessary libraries

```python
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc

from dash_express import DashExpress, Page
```

Next, you need to initialize an instance of the Dash Express application.

```python
app = DashExpress(
    logo='DashExpress',          # navbar logo, string or dict: {'dark':'path/to/darklogo.svg', 'light':...}
    cache=True,                  # flask_caching.Cache instance, dict or True (default: True)
    default_cache_timeout=3600,  # flask_caching.Cache timeout in seconds (default: 3600)
    app_shell=...,               # Appshell class for customization UI your app (default: BaseAppShell())
    # And standart Plotly Dash param
 )
```

The Dash Express object implements a Dash application with a pre-configured interface and automatic callback generation for quickly creating interactive multi-page web analytics applications.

## Page definition

Each application page is a separate object, an instance of the `dash_express' class.Page`. The page contains the source data for analysis, graph creation functions and a list of filters.


```python
page = Page(
    app=app,                    # DashExpress app
    url_path='/',               # page url
    name='Owerview',            # page name in navigation buttons
    get_df=get_df,              # function for getting pd.DataFrame
    title='Owerview',           # page title
    )
```

## Getting data

The 'get_df` function contains the logic of getting data: 

```python
get_df = lambda: pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
```

## Dashboard layout

Next, you need to determine the layout of the dashboard. we recommend using dmc.Grid and dmc.SimpleGrid

```python
page.layout = dmc.SimpleGrid(
    page.add_graph(h='100%',render_func=bar_func)
    )
```

The render_func parameter of the page.add_graph method is a graph generation function based on data from a DataFrame

```python
# The logic of drawing a graph
def bar_func(df):
    pv = pd.pivot_table(df, index='continent', values='lifeExp').reset_index()
    fig = go.Figure([go.Bar(x=pv['continent'], y=pv['lifeExp'])])
    return fig
```

The last action is to add filters, which is done by simply calling the page.add_filter method and specifying the filtering column.

```python
page.add_autofilter('continent', multi=True)
page.add_autofilter('country', multi=True)
page.add_autofilter('lifeExp', multi=True)
```

## App run

These actions are enough to create a fully functional dashboard, so you can run the application.


```python
app.run()
```

## Full code of the minimal application

```python
import pandas as pd
import plotly.graph_objects as go
import dash_mantine_components as dmc

from dash_express import DashExpress, Page


# Incorporate data
get_df = lambda: pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')

# Initialize the app
app = DashExpress(logo='DashExpress')

# Initialize the Page
page = Page(
    app=app,                    # DashExpress app
    url_path='/',               # page url
    name='Owerview',            # page name in navigation buttons
    get_df=get_df,              # function for getting pd.DataFrame
    title='Owerview',           # page title
    )

# The logic of drawing a graph
def bar_func(df):
    pv = pd.pivot_table(df, index='continent', values='lifeExp').reset_index()
    fig = go.Figure([go.Bar(x=pv['continent'], y=pv['lifeExp'])])
    return fig

# Dashboard layout
page.layout = dmc.SimpleGrid(
    page.add_graph(h='calc(100vh - 138px)',render_func=bar_func)
    )

# By which columns to filter
page.add_autofilter('continent', multi=True)
page.add_autofilter('country', multi=True)
page.add_autofilter('lifeExp', multi=True)

app.run(debug=True)
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