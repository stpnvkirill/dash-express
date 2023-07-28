import os
import json
import uuid
import random
import orjson

import numpy as np
import pandas as pd
import dash_leaflet as dl
import plotly.graph_objects as go
import dash_mantine_components as dmc


from .kpi import KPI, FastKPI
from .filters import autofilter
from flask_caching import Cache
from dash_iconify import DashIconify
from .preview_chart import _render_wrapper
from dash.exceptions import PreventUpdate
from dash._jupyter import JupyterDisplayMode
from ._app_shell import BaseAppShell, AsideAppShell
from dash import Dash, Output, Input, State, ALL, dcc, html, Patch, MATCH


_default_index = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <!--[if IE]><script>
        alert("Dash v2.7+ does not support Internet Explorer. Please use a newer browser.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""


class DashExpress(Dash):
    """The DashExpress object implements a Dash application with a pre-configured 
    interface and automatic generation of callbacks to quickly create interactive 
    multi-page web analytics applications.

    DashExpress uses the Mantine framework and supports dark theme out of the box. 
    Additionally on the side of DashExpress dark is applied to the objects of PLotly figures and Leaflet maps.
    
    Dash is a framework for building analytic web applications without 
    the use of JavaScript.
    
    :param name: The name Flask should use for your app. Even if you provide
        your own ``server``, ``name`` will be used to help find assets.
        Typically ``__name__`` (the magic global var, not a string) is the
        best value to use. Default ``'__main__'``, env: ``DASH_APP_NAME``
    :type name: string

    :param server: Sets the Flask server for your app. There are three options:
        ``True`` (default): Dash will create a new server
        ``False``: The server will be added later via ``app.init_app(server)``
            where ``server`` is a ``flask.Flask`` instance.
        ``flask.Flask``: use this pre-existing Flask server.
    :type server: boolean or flask.Flask

    :param assets_folder: a path, relative to the current working directory,
        for extra files to be used in the browser. Default ``'assets'``.
        All .js and .css files will be loaded immediately unless excluded by
        ``assets_ignore``, and other files such as images will be served if
        requested.
    :type assets_folder: string

    :param pages_folder: a relative or absolute path for pages of a multi-page app.
        Default ``'pages'``.
    :type pages_folder: string or pathlib.Path

    :param use_pages: When True, the ``pages`` feature for multi-page apps is
        enabled. If you set a non-default ``pages_folder`` this will be inferred
        to be True. Default `None`.
    :type use_pages: boolean

    :param include_pages_meta: Include the page meta tags for twitter cards.
    :type include_pages_meta: bool

    :param assets_url_path: The local urls for assets will be:
        ``requests_pathname_prefix + assets_url_path + '/' + asset_path``
        where ``asset_path`` is the path to a file inside ``assets_folder``.
        Default ``'assets'``.
    :type asset_url_path: string

    :param assets_ignore: A regex, as a string to pass to ``re.compile``, for
        assets to omit from immediate loading. Ignored files will still be
        served if specifically requested. You cannot use this to prevent access
        to sensitive files.
    :type assets_ignore: string

    :param assets_external_path: an absolute URL from which to load assets.
        Use with ``serve_locally=False``. assets_external_path is joined
        with assets_url_path to determine the absolute url to the
        asset folder. Dash can still find js and css to automatically load
        if you also keep local copies in your assets folder that Dash can index,
        but external serving can improve performance and reduce load on
        the Dash server.
        env: ``DASH_ASSETS_EXTERNAL_PATH``
    :type assets_external_path: string

    :param include_assets_files: Default ``True``, set to ``False`` to prevent
        immediate loading of any assets. Assets will still be served if
        specifically requested. You cannot use this to prevent access
        to sensitive files. env: ``DASH_INCLUDE_ASSETS_FILES``
    :type include_assets_files: boolean

    :param url_base_pathname: A local URL prefix to use app-wide.
        Default ``'/'``. Both `requests_pathname_prefix` and
        `routes_pathname_prefix` default to `url_base_pathname`.
        env: ``DASH_URL_BASE_PATHNAME``
    :type url_base_pathname: string

    :param requests_pathname_prefix: A local URL prefix for file requests.
        Defaults to `url_base_pathname`, and must end with
        `routes_pathname_prefix`. env: ``DASH_REQUESTS_PATHNAME_PREFIX``
    :type requests_pathname_prefix: string

    :param routes_pathname_prefix: A local URL prefix for JSON requests.
        Defaults to ``url_base_pathname``, and must start and end
        with ``'/'``. env: ``DASH_ROUTES_PATHNAME_PREFIX``
    :type routes_pathname_prefix: string

    :param serve_locally: If ``True`` (default), assets and dependencies
        (Dash and Component js and css) will be served from local URLs.
        If ``False`` we will use CDN links where available.
    :type serve_locally: boolean

    :param compress: Use gzip to compress files and data served by Flask.
        To use this option, you need to install dash[compress]
        Default ``False``
    :type compress: boolean

    :param meta_tags: html <meta> tags to be added to the index page.
        Each dict should have the attributes and values for one tag, eg:
        ``{'name': 'description', 'content': 'My App'}``
    :type meta_tags: list of dicts

    :param index_string: Override the standard Dash index page.
        Must contain the correct insertion markers to interpolate various
        content into it depending on the app config and components used.
        See https://dash.plotly.com/external-resources for details.
    :type index_string: string

    :param external_scripts: Additional JS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``src`` (the URL)
        and optionally other ``<script>`` tag attributes such as ``integrity``
        and ``crossorigin``.
    :type external_scripts: list of strings or dicts

    :param external_stylesheets: Additional CSS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``href`` (the URL)
        and optionally other ``<link>`` tag attributes such as ``rel``,
        ``integrity`` and ``crossorigin``.
    :type external_stylesheets: list of strings or dicts

    :param suppress_callback_exceptions: Default ``False``: check callbacks to
        ensure referenced IDs exist and props are valid. Set to ``True``
        if your layout is dynamic, to bypass these checks.
        env: ``DASH_SUPPRESS_CALLBACK_EXCEPTIONS``
    :type suppress_callback_exceptions: boolean

    :param prevent_initial_callbacks: Default ``False``: Sets the default value
        of ``prevent_initial_call`` for all callbacks added to the app.
        Normally all callbacks are fired when the associated outputs are first
        added to the page. You can disable this for individual callbacks by
        setting ``prevent_initial_call`` in their definitions, or set it
        ``True`` here in which case you must explicitly set it ``False`` for
        those callbacks you wish to have an initial call. This setting has no
        effect on triggering callbacks when their inputs change later on.

    :param show_undo_redo: Default ``False``, set to ``True`` to enable undo
        and redo buttons for stepping through the history of the app state.
    :type show_undo_redo: boolean

    :param extra_hot_reload_paths: A list of paths to watch for changes, in
        addition to assets and known Python and JS code, if hot reloading is
        enabled.
    :type extra_hot_reload_paths: list of strings

    :param plugins: Extend Dash functionality by passing a list of objects
        with a ``plug`` method, taking a single argument: this app, which will
        be called after the Flask server is attached.
    :type plugins: list of objects

    :param title: Default ``Dash``. Configures the document.title
    (the text that appears in a browser tab).

    :param update_title: Default ``Updating...``. Configures the document.title
    (the text that appears in a browser tab) text when a callback is being run.
    Set to None or '' if you don't want the document.title to change or if you
    want to control the document.title through a separate component or
    clientside callback.

    :param long_callback_manager: Deprecated, use ``background_callback_manager``
        instead.

    :param background_callback_manager: Background callback manager instance
        to support the ``@callback(..., background=True)`` decorator.
        One of ``DiskcacheManager`` or ``CeleryManager`` currently supported.

    :param add_log_handler: Automatically add a StreamHandler to the app logger
        if not added previously."""

    def __init__(self, logo='DashExpress', cache=True, default_cache_timeout=3600, app_shell=BaseAppShell(), name=None, server=True, assets_folder="assets", pages_folder="pages", 
                 use_pages=None, assets_url_path="assets", assets_ignore="", assets_external_path=None, eager_loading=False, 
                 include_assets_files=True, include_pages_meta=True, url_base_pathname=None, requests_pathname_prefix=None, 
                 routes_pathname_prefix=None, serve_locally=True, compress=None, meta_tags=None, index_string=_default_index, 
                 external_scripts=None, external_stylesheets=None, suppress_callback_exceptions=None, prevent_initial_callbacks=False, 
                 show_undo_redo=False, extra_hot_reload_paths=None, plugins=None, title="Dash", update_title="Updating...", 
                 long_callback_manager=None, background_callback_manager=None, add_log_handler=True, **obsolete):
        super().__init__(name, server, assets_folder, pages_folder, use_pages, assets_url_path, assets_ignore, assets_external_path, 
                         eager_loading, include_assets_files, include_pages_meta, url_base_pathname, requests_pathname_prefix, 
                         routes_pathname_prefix, serve_locally, compress, meta_tags, index_string, external_scripts, 
                         external_stylesheets, suppress_callback_exceptions, prevent_initial_callbacks, show_undo_redo, 
                         extra_hot_reload_paths, plugins, title, update_title, long_callback_manager, background_callback_manager, 
                         add_log_handler, **obsolete)
        self.PAGES = {}
        self.app_shell = app_shell
        self.app_shell.LOGO = logo
        self.default_cache_timeout = default_cache_timeout
        if isinstance(cache, Cache):
            self.cache = cache
        elif isinstance(cache, bool) and cache == True:
            self.cache = Cache(self.server, config={'CACHE_TYPE': 'SimpleCache'})
        elif isinstance(cache, dict):
            self.cache = Cache(self.server, config=cache)
        else:
            raise ValueError("cache must be a flask_caching.Cache or a boolean")
        
    def _app_shell(self):
        self.layout = self.app_shell._app_provider(self)

    def register_page(self, Page):
        self.PAGES[Page.URL] = Page
    
    def register_server_callback(self):
        """Register a function callback on the server side"""
        # Send Page.layout to front
        @self.callback(Output("layout-store", 'data'),
                    Input("layout-store", 'data'))
        def send_layout(d):
            dict1 = {k: v.render()
                    for k, v in self.PAGES.items() if v.is_accessible()}
            dict2 = {k: v.preview()for k, v in self.PAGES.items()
                    if not v.is_accessible() and v.access_mode == 'view'}
            dict3 = {'#error': [None, self.app_shell.ERROR_PAGE]}

            meta = {k:v.metatags() for k, v in self.PAGES.items()}

            return {'content':{**dict1, **dict2, **dict3}, 'navs': self.app_shell._build_navs(self), 'meta':meta}

        # Render Chart
        @self.callback([Output({'type': 'graph', 'id': ALL}, 'figure'),
                        Output({'type': 'kpi', 'id': ALL}, 'children'),
                        Output({'type': "geojson", 'id': ALL}, 'data')],
                    Input('contentfilter-store', 'data'),
                    State({'type': 'contentfilter-store', 'id': ALL}, 'id'),
                    State({'type': 'kpifilter-store', 'id': ALL}, 'id'),
                    State({'type': 'geojsonfilter-store', 'id': ALL}, 'id'),
                    State("url-store", 'pathname'))
        def s(filters, ids, ids_kpi, ids_geo, url):
            page = self.PAGES.get(url)
            if page:
                df = page.filtered(filters)
                res = []
                kpi = []
                geo = []
                for id in ids:
                    try:
                        fig = page.RENDER_FUNC.get(
                            id.get('id', 'default'))(df)
                    except:
                        fig = go.Figure()
                    patched_fig = Patch()
                    patched_fig.data = fig.data
                    patched_fig.layout.xaxis.autorange = True
                    patched_fig.layout.yaxis.autorange = True
                    res.append(patched_fig)
                for id in ids_kpi:
                    k = page.RENDER_FUNC_KPI.get(id.get('id', 'default'))(df)
                    kpi.append(k)
                for id in ids_geo:
                    g = page.GEOJSON_FUNC.get(id.get('id', 'default'))(df)
                    geo.append(g)
                return [res, kpi, geo]
            else:
                raise PreventUpdate

        if self.DOWNLOAD_OPPORTUNITY:
            # Send DataFrame
            @self.callback(Output({'type':'download-frame','page':MATCH}, 'data'),
                        Output({'type':'download-frame-action','page':MATCH}, 'color'),
                        Input({'type':'download-frame-action','page':MATCH}, 'n_clicks'),
                        State('contentfilter-store', 'data'),
                        State({'type':'download-frame-action','page':MATCH}, 'id'),
                        prevent_initial_call=False,
                        suppress_callback_exceptions=True,
                        #    running=[
                        #         (Output("download-frame-action", "loading"), True, False),
                        #     ],
                            )
            def send_frame(n_clicks, filters, url):
                if n_clicks is None:
                    raise PreventUpdate
                page = self.PAGES.get(url.get('page'))
                if page:
                    df = page.filtered(filters)
                    return dcc.send_data_frame(df.to_csv, "qweta_data.csv"), 'gray'
                return {}, 'gray'


        self.app_shell.app_shell_serverside(self)

    def register_clientside_callback(self):
        """Register a function callback on the client side"""  
        # Dark Theme
        self.clientside_callback(
            """ function(data, figs, maps) {
                    const maplayer = data["colorScheme"] == "dark" ? "%(dark_layer)s" : "%(light_layer)s";
                    const dark = %(dark)s ;
                    const light = %(light)s ;
                    for (var i = 0; i < figs.length; i++) {
                        figs[i] = Object.assign({}, figs[i], {
                            'layout': {
                                ...figs[i].layout,
                                'template': data["colorScheme"] == "dark" ?  dark : light}
                                }
                            );
                        };
                    for (var i = 0; i < maps.length; i++) {
                        maps[i] = maplayer 
                        };
                    return [data,maps,figs] } """ % dict(
                light=json.dumps(
                    self.app_shell.LIGHT_PLOTLY_TEMPLATES.to_plotly_json()),
                dark=json.dumps(
                    self.app_shell.DARK_PLOTLY_TEMPLATES.to_plotly_json()),
                dark_layer = self.app_shell.DARK_LEAFLET_TILE,
                light_layer = self.app_shell.LIGHT_LEAFLET_TILE,
            ),
            Output("mantine-docs-theme-provider", "theme"),
            Output(dict(type='map-layer',id=ALL), "url"),
            Output({'type': 'graph', 'id': ALL}, 'figure', allow_duplicate=True),
            Input("theme-store", "data"),
            Input({'type': 'graph', 'id': ALL}, 'figure'),
            State(dict(type='map-layer',id=ALL), "url"),
            prevent_initial_call=True
        )
        self.clientside_callback(
            """function(n_clicks, n_clicks1, data) {
                if (data) {
                    if (n_clicks || n_clicks1) {
                        const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                        return { colorScheme: scheme } 
                    }
                    return dash_clientside.no_update
                } else {
                    return { colorScheme: "dark" }
                }
            }""",
            Output("theme-store", "data"),
            Input("color-scheme-toggle", "n_clicks"),
            Input("color-scheme-toggle-dropdown", "n_clicks"),
            State("theme-store", "data"),
        )
        if isinstance(self.app_shell.LOGO, dict) and self.LOGO.get('type') == 'img':
            self.clientside_callback(
                """ function(data) {  
                            const logo = data["colorScheme"] == "dark" ? "%(dark_logo)s" : "%(light_logo)s";
                            return logo;
                    } """ % dict(
                        light_logo=self.LOGO.get('children', {}).get('light'),
                        dark_logo=self.LOGO.get('children', {}).get(
                            'dark') or self.LOGO.get('children', {}).get('light'),
                    ),
                    Output("logo-img", "src"),
                    Input("theme-store", "data"),
            )
    
        # Filters Store
        self.clientside_callback(
            '''function f(data, index) {
                var dct = {};
                for (var i = 0; i < index.length; i++) {
                if (data[i] != undefined) {
                    dct[index[i]['id']] = data[i]
                }
                };
                const icon = Object.keys(dct).length == 0 ? "mdi:filter" : "mdi:filter-check";
                return [dct, icon];
            }''',
            [Output('contentfilter-store', 'data'),
            Output('filter-wrapper-icon', 'icon')],
            Input({'type': 'filter', 'id': ALL}, 'value'),
            State({'type': 'filter', 'id': ALL}, 'id'))
        
        # Render Page.layout
        self.clientside_callback(
            """ function(url, layout) {             
                if (layout['meta'][url] != undefined) {
                    document.title = layout['meta'][url]['title'];
                    document.description = layout['meta'][url]['description'];
                } ;
                var res = layout['content'][url] == undefined ? layout['content']['#error']:layout['content'][url];            
                return res } """,
            [Output("sidebar-filter", 'children'),
            Output("page_layout", 'children')],
            Input("url-store", 'pathname'),
            Input("layout-store", 'data'))
        
        
        # Render Page.layout
        self.clientside_callback(
            """ function(layout) {                        
                return [layout['navs']] } """,
            [Output("nav-content", 'children')],
            Input("layout-store", 'data'))
        
        self.app_shell.app_shell_clientside(self)

    def compile_layout(self):
        self._app_shell()
        self.DOWNLOAD_OPPORTUNITY = np.any([page.download_opportunity for page in self.PAGES.values()])
        self.register_clientside_callback()
        self.register_server_callback()

    def run(self, host=os.getenv("HOST", "127.0.0.1"), port=os.getenv("PORT", "8050"), proxy=os.getenv("DASH_PROXY", None), debug=None,
            jupyter_mode: JupyterDisplayMode = None, jupyter_width="100%", jupyter_height=650, jupyter_server_url=None,
            dev_tools_ui=None, dev_tools_props_check=None, dev_tools_serve_dev_bundles=None, dev_tools_hot_reload=None,
            dev_tools_hot_reload_interval=None, dev_tools_hot_reload_watch_interval=None, dev_tools_hot_reload_max_retry=None,
            dev_tools_silence_routes_logging=None, dev_tools_prune_errors=None, **flask_run_options):
        
        self.compile_layout()
        return super().run(host, port, proxy, debug, jupyter_mode, jupyter_width, jupyter_height, jupyter_server_url, dev_tools_ui, 
                           dev_tools_props_check, dev_tools_serve_dev_bundles, dev_tools_hot_reload, dev_tools_hot_reload_interval, 
                           dev_tools_hot_reload_watch_interval, dev_tools_hot_reload_max_retry, dev_tools_silence_routes_logging, 
                           dev_tools_prune_errors, **flask_run_options)


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
        self.URL = url_path
        self.title = title if title else app.config['title']
        self.description = description
        self.access_func = access_func
        self.access_mode = access_mode
        self.download_opportunity = download_opportunity

        self.RENDER_FUNC = {}
        self.RENDER_FUNC_KPI = {}
        self.GEOJSON_FUNC = {}
        self.FILTERS = []
        self.FILTERS_FUNC = {}
        self.layout = dmc.Grid()

        if isinstance(app, DashExpress):
            self.app = app
            app.register_page(self)
        else:
            raise ValueError("param app must be a DashExpress app")
        
        if type(get_df) != type(None):
            self.register_frame(get_df)
        else:
            self.get_df_func = lambda: pd.DataFrame()     

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
        fig.update_layout(template=self.app.app_shell.DARK_PLOTLY_TEMPLATES)
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
                        [dl.TileLayer(url=self.app.app_shell.LIGHT_LEAFLET_TILE, id=dict(type='map-layer', id=id)),
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
