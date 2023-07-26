import uuid
import random

import pandas as pd
import dash_leaflet as dl
import dash_mantine_components as dmc

from dash import dcc, html
from dash_iconify import DashIconify
from .preview_chart import _render_wrapper
from .filters import select_filters, multiselect_filters, range_filters, autofilter


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
        self.get_df_func = self.app.cache_func(get_df)

    def add_kpi(self, kpi):
        id = str(uuid.uuid4())
        self.RENDER_FUNC_KPI[id] = kpi.render_func
        self.RENDER_FUNC_KPI['default'] = self.render_kpi_wrapper
        return kpi.render_layout(id)

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

    def add_map(self, p=0, geojson_func=None, dl_geojson_kwargs={'zoomToBounds': True}, **kwargs):
        id = str(uuid.uuid4())
        geojson_func = geojson_func or self.geojson_wrapper
        self.GEOJSON_FUNC[id] = geojson_func
        self.GEOJSON_FUNC['default'] = self.geojson_wrapper
        return dmc.LoadingOverlay(dmc.Card(
            [
                # dmc.CardSection(
                #     dmc.Title('Graph', order=5),
                #     withBorder=True,
                #     inheritPadding=True,
                #     py="xs",
                # ),
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
    def geojson_wrapper(df):
        return {}
        # geojson_str = """{
        # "type": "FeatureCollection",
        # "features": [
        #     {
        #     "type": "Feature",
        #     "properties": {},
        #     "geometry": {
        #         "coordinates": [
        #         82.83938144485796,
        #         55.01113717460842
        #         ],
        #         "type": "Point"
        #     }
        #     },
        #     {
        #     "type": "Feature",
        #     "properties": {},
        #     "geometry": {
        #         "coordinates": [
        #         82.91863762829416,
        #         55.080832168205234
        #         ],
        #         "type": "Point"
        #     }
        #     },
        #     {
        #     "type": "Feature",
        #     "properties": {},
        #     "geometry": {
        #         "type": "Polygon",
        #         "coordinates": [
        #         [
        #             [
        #             82.97761897373563,
        #             55.02542909072005
        #             ],
        #             [
        #             82.97318684963444,
        #             55.02530420059082
        #             ],
        #             [
        #             82.96879749148097,
        #             55.024930735285054
        #             ],
        #             [
        #             82.9644932501982,
        #             55.024312298353664
        #             ],
        #             [
        #             82.960315650779,
        #             55.023454856847316
        #             ],
        #             [
        #             82.95630498957446,
        #             55.02236668342025
        #             ],
        #             [
        #             82.95249994376304,
        #             55.0210582760814
        #             ],
        #             [
        #             82.94893719685577,
        #             55.01954225638764
        #             ],
        #             [
        #             82.94565108392162,
        #             55.01783324708737
        #             ],
        #             [
        #             82.94267326000751,
        #             55.01594773042337
        #             ],
        #             [
        #             82.94003239498058,
        #             55.0139038884935
        #             ],
        #             [
        #             82.93775389774306,
        #             55.01172142724136
        #             ],
        #             [
        #             82.93585967246294,
        #             55.009421385807315
        #             ],
        #             [
        #             82.93436790913124,
        #             55.00702593310868
        #             ],
        #             [
        #             82.933292910405,
        #             55.00455815363976
        #             ],
        #             [
        #             82.93264495632447,
        #             55.00204182458087
        #             ],
        #             [
        #             82.93243020811296,
        #             54.99950118638515
        #             ],
        #             [
        #             82.93265065187724,
        #             54.996960709068915
        #             ],
        #             [
        #             82.933304082634,
        #             54.99444485646599
        #             ],
        #             [
        #             82.93438412869453,
        #             54.99197785071964
        #             ],
        #             [
        #             82.93588031605263,
        #             54.989583439276494
        #             ],
        #             [
        #             82.93777817203846,
        #             54.98728466661602
        #             ],
        #             [
        #             82.9400593671349,
        #             54.985103652897386
        #             ],
        #             [
        #             82.94270189349659,
        #             54.98306138163308
        #             ],
        #             [
        #             82.94568027837688,
        #             54.98117749840696
        #             ],
        #             [
        #             82.94896583035066,
        #             54.979470122544775
        #             ],
        #             [
        #             82.95252691592812,
        #             54.977955673517194
        #             ],
        #             [
        #             82.95632926388386,
        #             54.976648713712756
        #             ],
        #             [
        #             82.96033629438385,
        #             54.97556180906036
        #             ],
        #             [
        #             82.96450946977552,
        #             54.974705408810564
        #             ],
        #             [
        #             82.96880866372068,
        #             54.97408774560266
        #             ],
        #             [
        #             82.97319254519303,
        #             54.97371475675349
        #             ],
        #             [
        #             82.97761897373563,
        #             54.97359002750396
        #             ],
        #             [
        #             82.98204540227823,
        #             54.97371475675349
        #             ],
        #             [
        #             82.98642928375055,
        #             54.97408774560266
        #             ],
        #             [
        #             82.99072847769573,
        #             54.974705408810564
        #             ],
        #             [
        #             82.99490165308738,
        #             54.97556180906036
        #             ],
        #             [
        #             82.99890868358737,
        #             54.976648713712756
        #             ],
        #             [
        #             83.00271103154314,
        #             54.977955673517194
        #             ],
        #             [
        #             83.00627211712057,
        #             54.979470122544775
        #             ],
        #             [
        #             83.00955766909436,
        #             54.98117749840696
        #             ],
        #             [
        #             83.01253605397463,
        #             54.98306138163308
        #             ],
        #             [
        #             83.01517858033637,
        #             54.985103652897386
        #             ],
        #             [
        #             83.0174597754328,
        #             54.98728466661602
        #             ],
        #             [
        #             83.01935763141861,
        #             54.989583439276494
        #             ],
        #             [
        #             83.0208538187767,
        #             54.99197785071964
        #             ],
        #             [
        #             83.02193386483725,
        #             54.99444485646599
        #             ],
        #             [
        #             83.02258729559401,
        #             54.996960709068915
        #             ],
        #             [
        #             83.02280773935829,
        #             54.99950118638515
        #             ],
        #             [
        #             83.02259299114677,
        #             55.00204182458087
        #             ],
        #             [
        #             83.02194503706623,
        #             55.00455815363976
        #             ],
        #             [
        #             83.02087003834,
        #             55.00702593310868
        #             ],
        #             [
        #             83.01937827500832,
        #             55.009421385807315
        #             ],
        #             [
        #             83.01748404972818,
        #             55.01172142724136
        #             ],
        #             [
        #             83.01520555249066,
        #             55.0139038884935
        #             ],
        #             [
        #             83.01256468746374,
        #             55.01594773042337
        #             ],
        #             [
        #             83.00958686354961,
        #             55.01783324708737
        #             ],
        #             [
        #             83.00630075061548,
        #             55.01954225638764
        #             ],
        #             [
        #             83.00273800370819,
        #             55.0210582760814
        #             ],
        #             [
        #             82.99893295789677,
        #             55.02236668342025
        #             ],
        #             [
        #             82.99492229669225,
        #             55.023454856847316
        #             ],
        #             [
        #             82.99074469727303,
        #             55.024312298353664
        #             ],
        #             [
        #             82.98644045599026,
        #             55.024930735285054
        #             ],
        #             [
        #             82.98205109783679,
        #             55.02530420059082
        #             ],
        #             [
        #             82.97761897373563,
        #             55.02542909072005
        #             ]
        #         ]
        #         ]
        #     }
        #     }
        # ]
        # }"""

        # gdf = gpd.read_file(geojson_str, driver='GeoJSON')

        # return gdf.__geo_interface__

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
