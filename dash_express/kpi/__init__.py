import dash_mantine_components as dmc
from dash_iconify import DashIconify
from dash import html, dcc
import numpy as np


class KPI(object):
    def __init__(self, title, func, icon="flat-ui:settings", **kwargs) -> None:
        self.title = title
        self.func = func
        self.icon = icon
        self.kwargs = kwargs

    def render_layout(self, id):
        return dmc.Card(
            dmc.Stack(
                [
                    dmc.Group([
                        dmc.Text(self.title, size="xl", color="dimmed"),
                        DashIconify(icon=self.icon, width=30),], position="apart"),
                    html.Div([
                        dmc.Group(align="flex-end", spacing="xs", mt=25,
                                id=dict(type='kpi', id=id)),
                        dmc.Text('Compared to previous month',
                                fz="xs", c="dimmed", mt=7)]),
                    dcc.Store(id=id)
                ], justify="space-around", spacing=0),
            withBorder=True,
            radius='md',
            p="md",
            **self.kwargs)

    def render_func(self,df):
        return self.func(df)
    

class FastKPI(KPI):
    def __init__(self, col, agg_func=np.mean, pretty_func=lambda x: f'{x:.1%}', title='auto', 
                 icon="flat-ui:settings", **kwargs) -> None:
        if title == 'auto':
            title = col.capitalize()
        func = self.render_fastkpi_wrapper(col, agg_func, pretty_func=pretty_func)
        super().__init__(title, func, icon=icon, **kwargs)

    def render_fastkpi_wrapper(self, col, agg_func, pretty_func):
        def wrapper(df):
            value = pretty_func(agg_func(df[col]))
            return [dmc.Text(value, size=35)]
        return wrapper
