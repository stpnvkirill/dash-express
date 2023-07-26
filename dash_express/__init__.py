import os
import json

import numpy as np
import plotly.io as pio
import dash_mantine_components as dmc


from ._page import Page
from .kpi import KPI, FastKPI
from functools import lru_cache
from dash.exceptions import PreventUpdate
from dash._jupyter import JupyterDisplayMode
from ._app_shell import BaseAppShell, AsideAppShell
from dash import Dash, Output, Input, State, ALL, dcc, html, Patch, MATCH


m = 15
margin = dict(l=m, r=m, t=round(3.5*m), b=m)
DARK_PLOTLY_TEMPLATES = pio.templates["plotly_dark"]
DARK_PLOTLY_TEMPLATES['layout']['paper_bgcolor'] = 'rgba(0,0,0,0)'
DARK_PLOTLY_TEMPLATES['layout']['plot_bgcolor'] = 'rgba(0,0,0,0)'
DARK_PLOTLY_TEMPLATES['layout']['margin'] = margin

LIGHT_PLOTLY_TEMPLATES = pio.templates["plotly_white"]
LIGHT_PLOTLY_TEMPLATES['layout']['paper_bgcolor'] = 'rgba(0,0,0,0)'
LIGHT_PLOTLY_TEMPLATES['layout']['plot_bgcolor'] = 'rgba(0,0,0,0)'
LIGHT_PLOTLY_TEMPLATES['layout']['margin'] = margin

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
    """The HyperDash object implements a Dash application with a pre-configured 
    interface and automatic generation of callbacks to quickly create interactive 
    multi-page web analytics applications.

    HyperDash uses the Mantine framework and supports dark theme out of the box. 
    Additionally on the side of HyperDash dark is applied to the objects of PLotly figures and Leaflet maps.
    
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

    PRIMARY_COLORS = 'red'
    THEME = {
        "colors": {
            "myPrimaryColor": [
                "#65BC46",
            ] * 10
        },
        "fontFamily": "'Inter', sans-serif",
        "primaryColor": PRIMARY_COLORS,
        "components": {
            # "Card": {"styles": {"root":{"backgroundColor": 'rgb(18 18 18)'}}},
        },
    }

    PAGES = {}

    LOGO = {'type':'img', 'children':{'dark':'/assets/logo/darklogo.svg','light':'/assets/logo/lightlogo.svg'}}

    LIGHT_PLOTLY_TEMPLATES = LIGHT_PLOTLY_TEMPLATES
    DARK_PLOTLY_TEMPLATES = DARK_PLOTLY_TEMPLATES
    DARK_LEAFLET_TILE = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
    LIGHT_LEAFLET_TILE = 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

    ERROR_PAGE = dmc.Stack(
                align="center",
                children=[
                    dmc.Text(
                        [
                            "If you think this page should exist, create an issue ",
                            dmc.Anchor(
                                "here",
                                underline=False,
                                href="https://github.com/thedirtyfew/dash-extensions/issues/new",
                            ),
                            ".",
                        ]
                    ),
                    dmc.Anchor("Go back to home ->",
                               href="/", underline=False),
                ],
            )

    def __init__(self, app_shell=BaseAppShell(), name=None, server=True, assets_folder="assets", pages_folder="pages", use_pages=None, assets_url_path="assets", assets_ignore="", assets_external_path=None, eager_loading=False, include_assets_files=True, include_pages_meta=True, url_base_pathname=None, requests_pathname_prefix=None, routes_pathname_prefix=None, serve_locally=True, compress=None, meta_tags=None, index_string=_default_index, external_scripts=None, external_stylesheets=None, suppress_callback_exceptions=None, prevent_initial_callbacks=False, show_undo_redo=False, extra_hot_reload_paths=None, plugins=None, title="Dash", update_title="Updating...", long_callback_manager=None, background_callback_manager=None, add_log_handler=True, **obsolete):
        self.app_shell = app_shell
        super().__init__(name, server, assets_folder, pages_folder, use_pages, assets_url_path, assets_ignore, assets_external_path, eager_loading, include_assets_files, include_pages_meta, url_base_pathname, requests_pathname_prefix, routes_pathname_prefix, serve_locally, compress, meta_tags, index_string, external_scripts, external_stylesheets, suppress_callback_exceptions, prevent_initial_callbacks, show_undo_redo, extra_hot_reload_paths, plugins, title, update_title, long_callback_manager, background_callback_manager, add_log_handler, **obsolete)

    def _app_shell(self):
        self.layout = self.app_shell._app_provider(self)

    def regester_page(self, Page):
        self.PAGES[Page.URL] = Page

    def cache_func(self,f):
        return lru_cache(f)
    
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
            dict3 = {'#error': [None, self.ERROR_PAGE]}

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
                    fig = page.RENDER_FUNC.get(
                        id.get('id', 'default'))(df)
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
                    self.LIGHT_PLOTLY_TEMPLATES.to_plotly_json()),
                dark=json.dumps(
                    self.DARK_PLOTLY_TEMPLATES.to_plotly_json()),
                dark_layer = self.DARK_LEAFLET_TILE,
                light_layer = self.LIGHT_LEAFLET_TILE,
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
        if self.LOGO.get('type') == 'img':
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
        return super().run(host, port, proxy, debug, jupyter_mode, jupyter_width, jupyter_height, jupyter_server_url, dev_tools_ui, dev_tools_props_check, dev_tools_serve_dev_bundles, dev_tools_hot_reload, dev_tools_hot_reload_interval, dev_tools_hot_reload_watch_interval, dev_tools_hot_reload_max_retry, dev_tools_silence_routes_logging, dev_tools_prune_errors, **flask_run_options)