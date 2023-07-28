import uuid
import random

import pandas as pd
import dash_leaflet as dl
import dash_mantine_components as dmc

from dash import dcc, html
from .filters import autofilter
from dash_iconify import DashIconify
from .preview_chart import _render_wrapper


class Page(object):  
    """Page object for quickly creating a web dashboard.
        The app needs 3 components to work:

        1) DataFrame get function

        2) Dashboard layout

        3) Functions for generating graphs, kpi values ​​and getting geojson
        """  
    def __repr__(self):
        return f'Page: {self.URL}'

    def __init__(self, app, url_path, name=None, get_df=None, title=None, description=None,
                 access_func=None, access_mode='hide', download_opportunity=True,):
        self.name = name or 'Page'
        self.app = app
        self.URL = url_path
        self.title = title if title else app.config['title']
        self.description = description
        if type(get_df) != type(None):
            self.register_frame(get_df)
        else:
            self.get_df_func = lambda: pd.DataFrame()

        self.access_func = access_func
        self.access_mode = access_mode
        self.download_opportunity = download_opportunity

        self.RENDER_FUNC = {}
        self.RENDER_FUNC_KPI = {}
        self.GEOJSON_FUNC = {}
        self.FILTERS = []
        self.FILTERS_FUNC = {}

        html.Div()

        self.layout = dmc.Grid()

    def is_accessible(self):
        if self.access_func != None:
            return self.access_func()
        return True

    def render(self):
        filters = [
            dmc.CardSection(
                dmc.Group(
                    children=[
                        dmc.Title('Фильтры', order=3),
                        dmc.LoadingOverlay(
                            dmc.Tooltip(
                                multiline=True,
                                width=220,
                                withArrow=True,
                                transition="fade",
                                transitionDuration=200,
                                label="Скачать данные в виде таблицы",
                                children=[dmc.ActionIcon(
                                    DashIconify(
                                        icon="line-md:download-loop", height=25),
                                    color="gray",
                                    id={'type': 'download-frame-action',
                                        'page': self.URL},
                                    variant="transparent",
                                ), dcc.Download(id={'type': 'download-frame', 'page': self.URL})],
                            )) if self.download_opportunity else html.Div()], position="apart"),
                withBorder=True,
                inheritPadding=True,
                p='md',
                py=8,
            ),
            dmc.Stack(
                self.FILTERS,
                mt=15),
        ]
        page_content = self.layout
        return [filters, page_content]

    def preview(self):
        filters = [
            dmc.CardSection(
                dmc.Group(
                    children=[
                        dmc.Title('Фильтры', order=3),
                        dmc.LoadingOverlay(dmc.ActionIcon(
                            DashIconify(
                                icon="line-md:download-off-loop", height=25),
                            color="gray",
                            variant="transparent",
                        )) if self.download_opportunity else html.Div()], position="apart"),
                withBorder=True, 
                inheritPadding=True,
                p='md',
                py=8,
            ),
            dmc.Stack(
                self.FILTERS if len(self.FILTERS) > 0 else [
                    dmc.Skeleton(h=70) for i in range(4)],
                mt=15),
        ]
        page_content = self.get_prewiew_layout()
        return [filters, page_content]
    
    def metatags(self):
        return {'title':self.title, 'description':self.description}

    def register_frame(self, get_df):
        @self.app.cache.cached(timeout = self.app.default_cache_timeout, key_prefix=str(self) + '/')
        def get_df_func():
            df = get_df()
            return df  
                
        self.get_df_func = get_df_func

           
    def add_kpi(self, kpi):
        id = str(uuid.uuid4())
        self.RENDER_FUNC_KPI[id] = kpi.render_func
        self.RENDER_FUNC_KPI['default'] = self.render_kpi_wrapper
        return kpi.render_layout(dict(type='kpifilter-store', id=id))

    def add_graph(self, id=None, render_func=None, **kwargs):
        CONFIG = {
            'modeBarButtonsToRemove': ['pan2d', 'lasso2d',
                                    'logo', 
                                    'zoom',
                                    'box', 'select',
                                    # 'zoomin', 'zoomout', 
                                    'reset',
                                    'autoscale', 
                                    # 'resetaxes'
                                    ],
            'toImageButtonOptions': dict(
                format="webp",
            ),
            'displaylogo': False}
        render_func = render_func or self.render_wrapper()
        id = id or str(uuid.uuid4())
        self.RENDER_FUNC[id] = render_func
        self.RENDER_FUNC['default'] = self.render_wrapper()
        with self.app.server.app_context():
            fig = render_func(self.get_df_func())
            fig.data = []
        fig.update_layout(template=self.app.DARK_PLOTLY_TEMPLATES)
        return dmc.LoadingOverlay(dmc.Card(
            [
                dcc.Graph(figure=fig, id=dict(type='graph', id=id),
                          style={'height': '100%',
                                 # 'padding-bottom': '25px'
                                 },
                        config=CONFIG),

                dcc.Store(id=dict(type='contentfilter-store', id=id))
            ],
            withBorder=True,
            **kwargs
        ))

    def add_map(self, geojson_func=None, p=0, dl_geojson_kwargs={'zoomToBounds': True}, **kwargs):
        id = str(uuid.uuid4())
        geojson_func = geojson_func or self.geojson_wrapper
        self.GEOJSON_FUNC[id] = geojson_func
        self.GEOJSON_FUNC['default'] = self.geojson_wrapper
        return dmc.LoadingOverlay(dmc.Card(
            [
                html.Div(
                    dl.Map(
                        [dl.TileLayer(url=self.app.LIGHT_LEAFLET_TILE, id=dict(type='map-layer', id=id)),
                         dl.GeoJSON(id={'type': "geojson", 'id': id}, **dl_geojson_kwargs),],
                        markerZoomAnimation=True,
                        style={'height': '100%', 'width': '100%',
                               'z-index': '2'},
                        id='map-container',
                        bounds=[[55.072, 82.907], [54.92, 82.97]],
                        attributionControl=False
                    ), style={'height': '100%', 'width': '100%'}),
                dcc.Store(id=dict(type='geojsonfilter-store', id=id))
            ],
            withBorder=True,
            p=p,
            **kwargs
        ))

    def add_autofilter(self, col,  multi=False, type='auto', label='auto', **kwargs):

        filter_func, f = self._add_autofilter(
            col, multi, type, label, **kwargs)
        self.FILTERS_FUNC[col] = filter_func
        self.FILTERS.append(f)

    def _add_autofilter(self, col, multi=False, type='auto', label='auto', **kwargs):
        with self.app.server.app_context():
            serias = self.get_df_func()[col]
            if type == 'auto':
                data_type = str(serias.dtype)
                for dtype in ['int', 'float', 'object', 'str', 'datetime', 'category']:
                    if dtype in data_type:
                        type = 'slider' if dtype in [
                            'int', 'float'] else 'datepicker' if dtype == 'datetime' else 'select' 
                        return autofilter(type, serias, col, multi, label=label, **kwargs)
                for dtype in ['datetime', 'float', 'object', 'str']:
                    if dtype in data_type:
                        type = 'slider' if dtype in [
                            'int', 'float'] else 'select'
                        return autofilter(type, serias, col, multi, label=label, **kwargs)
            return autofilter(type, serias, col, multi, label=label, **kwargs)

    def filtered(self, filters):
        df = self.get_df_func()
        for k, v in filters.items():
            if v == None or (type(v) == type(list()) and len(v) == 0):
                continue
            df = df[self.FILTERS_FUNC[k](df[k], v)]
        return df

    @staticmethod
    def render_wrapper():
        return _render_wrapper()

    @staticmethod
    def render_kpi_wrapper(df):
        value, percent = random.randint(
            3456, 99999), random.randint(-200, 200)/1000
        return [dmc.Text(value, size=35),
                dmc.Text(html.Span(
                    f'{percent:.1%}'), fz="sm", fw=500, color='red' if percent < 0 else 'green', size="lg", mb='sm')]

    @staticmethod
    def geojson_wrapper(gdf):
        """
        def geojson(df):
            geojson_str = ...
        
            gdf = gpd.read_file(geojson_str, driver='GeoJSON')
        
            return gdf.__geo_interface__"""
        return gdf.__geo_interface__
        

    def get_prewiew_layout(self):
        PRIMARY_COL_HEIGHT = 'calc((100vh - 140px)*0.8 - 165px)'
        SECONDARY_COL_HEIGHT = 'calc((100vh - 140px)*0.8/2 - 90px)'
        PRIMARY_COL_HEIGHT_MIN = 100  # 800 *0.8 - 15
        SECONDARY_COL_HEIGHT_MIN = 100  # 800 *0.8/2 - 16
        CARD_COL_HEIGHT = 'calc((100vh - 140px)*0.8/4)'
        CARD_COL_HEIGHT_MIN = 100  # 800 *0.8/4
        return html.Div(
            [
                dmc.Alert(
                    "Этот отчет доступен только подписчикам ",
                    title="Доступ ограничен!",
                    id="alert-dismiss",
                    color="red",
                    withCloseButton=True,
                    mb=15,
                ),
                dmc.SimpleGrid(
                    cols=4,
                    spacing="md",
                    breakpoints=[{'maxWidth': 'sm', 'cols': 2}],
                    children=[dmc.Skeleton(
                        h=CARD_COL_HEIGHT, mih=CARD_COL_HEIGHT_MIN) for i in range(4)]
                ),
                dmc.SimpleGrid(
                    pt=15,
                    cols=2,
                    spacing="md",
                    breakpoints=[{'maxWidth': 'sm', 'cols': 1}],
                    children=[
                            dmc.Skeleton(h=PRIMARY_COL_HEIGHT,
                                         mih=PRIMARY_COL_HEIGHT_MIN),
                            dmc.SimpleGrid(
                                cols=1,
                                spacing="md",
                                children=[
                                        dmc.Skeleton(
                                            h=SECONDARY_COL_HEIGHT, mih=SECONDARY_COL_HEIGHT_MIN),
                                        dmc.SimpleGrid(
                                            cols=2,
                                            spacing="md",
                                            breakpoints=[
                                                {'maxWidth': 'sm', 'cols': 1}],
                                            children=[
                                                dmc.Skeleton(
                                                    h=SECONDARY_COL_HEIGHT, mih=SECONDARY_COL_HEIGHT_MIN),

                                                dmc.Skeleton(
                                                    h=SECONDARY_COL_HEIGHT, mih=SECONDARY_COL_HEIGHT_MIN),
                                            ])]
                            )
                    ]
                )
            ])
