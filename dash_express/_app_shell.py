import plotly.io as pio
import dash_mantine_components as dmc

from dash_iconify import DashIconify
from dash import html, dcc, Output, Input, State, ALL


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

class AppShell(object):
    def __init__(self, 
                primary_colors='indigo',
                theme=None,
                default_colorscheme='light',
                light_plotly_templates=None,
                dark_plotly_templates=None,
                dark_leaflet_tile=None,
                light_leaflet_tile=None,
                autocolorway=True,
                theme_icon_dark="line-md:moon-filled-alt-to-sunny-filled-loop-transition", 
                theme_icon_light="line-md:sunny-filled-loop-to-moon-filled-loop-transition"):
        self.PRIMARY_COLORS = primary_colors
        self.THEME = theme or {}
        self.THEME["primaryColor"] = self.PRIMARY_COLORS
        self.DEFAULT_THEME = default_colorscheme
        self.NAV_BUTTON_KWARGS = dict(color='primary',
                                p=3, miw=50, variant='subtle')
        self.THEME_ICON = {'dark': theme_icon_dark,"light": theme_icon_light}
        self.THEME_ICON_COLOR = {'dark': "gray",
                            "light": "yellow"}
        
        self.LIGHT_PLOTLY_TEMPLATES = light_plotly_templates or LIGHT_PLOTLY_TEMPLATES
        self.DARK_PLOTLY_TEMPLATES = dark_plotly_templates or DARK_PLOTLY_TEMPLATES
        self.DARK_LEAFLET_TILE = dark_leaflet_tile or 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
        self.LIGHT_LEAFLET_TILE = light_leaflet_tile or 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png'

                
        if autocolorway:
            self.autocolorway()

    def autocolorway(self):
        """Create a color path based on the primary color"""
        primarycolors = self.PRIMARY_COLORS
        lst = [[k, v[-1]] for k, v in dmc.theme.DEFAULT_COLORS.items()]
        colorway = list(sorted(lst, key = lambda x: '#zzzz' if (x[0] == primarycolors) else x[1], reverse=True))
        colorway = [i[1].upper() for i in colorway][:10]
        self.LIGHT_PLOTLY_TEMPLATES['layout']['colorway'] = colorway
        self.DARK_PLOTLY_TEMPLATES['layout']['colorway']  = colorway

    def build_nav_name(self, name, access):
        """Get the name of the navigation button"""
        name = [name, dmc.Group(DashIconify(icon="majesticons:lock"), ml=3)
                ] if not access else name
        return name

    def _build_nav(self, page):
        """Get the navigation button"""
        nav_name = self.build_nav_name(page.name, page.is_accessible())
        nav = dmc.Button(nav_name, **self.NAV_BUTTON_KWARGS)
        nav.id = dict(type='nav-link', href=str(page.URL))
        return dmc.Anchor(nav, href=page.URL, pt=4)

    def _build_navs(self, app):
        """Get a list of all available navigation buttons"""
        navs = [self._build_nav(page) for page in app.PAGES.values() if page.is_accessible(
        ) or page.access_mode == 'view']

        def filters(e):
            if e != None:
                return True
            else:
                return False

        out_filter = list(filter(filters, navs))
        return out_filter
    
    def logo_container(self, app):
        """Get a logo for the navigation bar
        
        :param app: DashExpress app

        Example:
        ```python
        dmc.Header(
            height=60, children=[self.logo_container(app),]
        )
        ```
        """
        return dmc.Anchor(
            dmc.Image(height=45, id='logo-img') if isinstance(self.LOGO, dict) else self.LOGO,
            weight=550,
            size=30,
            href=self.url_base(app),
            underline=False,
            pr='xl',
        ) if self.LOGO else html.Div()
    
    def color_scheme_toggle(self, icon, **kwargs):
        """Get a color scheme switch
        
        :param icon: icon for dmc.ActionIcon
        :type icon: DashIconify

        Example:
        ```python
        dmc.MediaQuery(
            self.color_scheme_toggle(
                icon=DashIconify(
                    icon="", width=22                                        
                ),
                variant="outline",
                radius='sm',
                size='lg',
            ),
            smallerThan="lg",
            styles={"display": "none"},

        )
        ```
        """
        icon.id = 'color-scheme-icon'
        action_icon = dmc.ActionIcon(icon, **kwargs)
        action_icon.id = "color-scheme-toggle"
        return action_icon

    def filter_wrapper_toggle(self, icon, **kwargs):
        """Get a filter wrapper switch
        
        :param icon: icon for dmc.ActionIcon
        :type icon: DashIconify

        Example:
        ```python
       dmc.MediaQuery(
            self.filter_wrapper_toggle(
                DashIconify(
                    icon="", width=22,
                    id='filter-wrapper-icon'
                ),
                variant="outline",
                radius='sm',
                size='lg',
                color='indigo',
            ),
            smallerThan="lg",
            styles={"display": "none"},
        )
        ```
        """
        action_icon = dmc.ActionIcon(icon, **kwargs)
        action_icon.id = "filter-wrapper-toggle"
        return action_icon
 
    def filter_wrapper(self):
        """Get a container with filters"""
        return html.Div([html.Div(id="sidebar-filter"), 
                dcc.Store(id='filter-wrapper-store')])
 
    def dashboard_wrapper(self):
        """Get a container with dashboard"""
        return html.Div(id='page_layout')

    def _build_menulink(self, page):
        """Get a button for the mobile menu"""
        icon = 'tabler:shield-lock' if not page.is_accessible() else 'tabler:arrow-big-right-lines'
        return dmc.MenuItem(
            page.name,
            id=dict(type='nav-link-menu', href=page.URL),
            icon=DashIconify(icon=icon), href=page.URL, py=5
        )

    def _build_menulinks(self, app):
        """Get a drop-down list for the mobile menu"""
        navs = [self._build_menulink(page) for page in app.PAGES.values() if page.is_accessible(
        ) or page.access_mode == 'view']

        def filters(e):
            if e != None:
                return True
            else:
                return False

        out_filter = list(filter(filters, navs))
        return dmc.MenuDropdown(
            [
                dmc.MenuLabel("Application", miw=200, py=5),
                dmc.MenuItem("Filters", icon=DashIconify(icon="tabler:filter"),
                             id="filter-wrapper-dropdown", py=5,),
                dmc.MenuItem("Color", icon=DashIconify(
                    icon="tabler:sun"), id="color-scheme-toggle-dropdown", py=5),
                dmc.MenuDivider(),
                dmc.MenuLabel("Pages", miw=200, py=5),
            ] + out_filter,
            miw=200,
            style={'z-index': '30000'}
        )

    def _app_provider(self, app):
        """get the primary downloadable component

        !Do not change"""
        return dmc.MantineProvider(
            dmc.MantineProvider(
                theme=self.THEME,
                inherit=True,
                children=[
                    dcc.Store(id="theme-store", storage_type="local"),
                    dcc.Store(id="layout-store", storage_type="local"),
                    dcc.Store(id="filter-store", storage_type="local"),
                    dcc.Store(id="page-store"),
                    dcc.Store(id='contentfilter-store'),
                    dcc.Location(id='url-store'),
                    self.render(app)
                ]
            ),
            theme={"colorScheme": self.DEFAULT_THEME},
            id="mantine-docs-theme-provider",
            withGlobalStyles=True,
            withNormalizeCSS=True,
        )
    
    def base_clientside(self, app):
        """Basic callback functions on the client side"""
        # Theme addition
        app.clientside_callback(
            """ function(data) {  
                const icon = data["colorScheme"] == "dark" ? "%(dark_icon)s" : "%(light_icon)s";
                const color = data["colorScheme"] != "dark" ? "%(dark_color)s" : "%(light_color)s";
                return [icon, color]                
              } """ % dict(
                dark_icon=self.THEME_ICON.get('dark'),
                light_icon=self.THEME_ICON.get('light'),
                dark_color=self.THEME_ICON_COLOR.get('dark'),
                light_color=self.THEME_ICON_COLOR.get('light')

            ),
            Output("color-scheme-icon", "icon"),
            Output("color-scheme-toggle", "color"),
            Input("theme-store", "data"),
        )
        # Nav-link variant
        app.clientside_callback(
            """ function(url, href) { 
                const res = [];  
                const res2 = []        
                for (var i = 0; i < href.length; i++) {
                    res[i] = href[i]["href"] == url ? 'light':'subtle'
                };
                for (var i = 0; i < href.length; i++) {
                    res2[i] = href[i]["href"] == url ? 'indigo':undefined
                };            
                return [res, res2] } """,
            [Output({'type': 'nav-link', 'href': ALL}, 'variant'),
             Output({'type': 'nav-link-menu', 'href': ALL}, 'color')],
            Input("url-store", 'pathname'),
            State({'type': 'nav-link', 'href': ALL}, 'id'))

    def nav_items_container(self, orientation='h'):
        """Get navigation buttons"""
        if orientation=='h':
            return dmc.Group(
                            id='nav-content',
                            spacing=3,
                        )
        else:
             return dmc.Stack(
                            id='nav-content',
                            spacing=3,
                        )

    def url_base(self, app):
        """Get a link to the home page"""
        return app.config.get('_pathname') or '/'

    def error_page(self, app):
        """Get the error page"""
        return dmc.Stack(
                    align="center",
                    children=[
                        dmc.Text(
                            [
                                "404 Not Found",
                            ]
                        ),
                        dmc.Anchor("Go back to home ->",
                                href=self.url_base(app), underline=False),
                    ],
                )

    def mobile_menu(self, app):
        """Get a menu for mobile devices"""
        return dmc.Menu(
            [
                dmc.MenuTarget(
                    dmc.ActionIcon(
                        DashIconify(
                            icon="line-md:close-to-menu-alt-transition",
                            width=18,
                        ),
                        variant="outline",
                        radius='sm',
                        size='lg',
                    )),
                self._build_menulinks(app),
            ],
            position="bottom-end",
            offset=5
        )
    
class BaseAppShell(AppShell):
    def nav_content(self, app):
        nav_cont = dmc.Grid(
            justify="center",
            style={"height": 60},
            children=[
                dmc.Col(
                    dmc.Group([
                        self.logo_container(app),
                        dmc.MediaQuery(
                            self.nav_items_container(orientation='h'), 
                            smallerThan="lg", 
                            styles={"display": "none"}, ),
                    ]),
                    pt=7,
                    span="content",
                ),
                dmc.Col(
                    span="auto",
                    children=dmc.Group(
                        pt=3,
                        position="right",
                        spacing="8px",
                        children=[
                            dmc.MediaQuery(
                                self.filter_wrapper_toggle(
                                    DashIconify(
                                        icon="", width=22,
                                        id='filter-wrapper-icon'
                                    ),
                                    variant="outline",
                                    radius='sm',
                                    size='lg',
                                    color='indigo',
                                ),
                                smallerThan="lg",
                                styles={"display": "none"},
                            ),
                            dmc.MediaQuery(
                                self.color_scheme_toggle(
                                    icon=DashIconify(
                                        icon="", width=22                                        
                                    ),
                                    variant="outline",
                                    radius='sm',
                                    size='lg',
                                ),
                                smallerThan="lg",
                                styles={"display": "none"},

                            ),
                            dmc.MediaQuery(
                                self.mobile_menu(app),
                                largerThan="lg",
                                styles={"display": "none"},
                            ),
                        ],
                    ),
                ),
            ],
        )
        return nav_cont

    def navbar(self, app):
        """Create a navigation panel layout"""
        navbar = dmc.Card(self.nav_content(app), radius='md',
                          withBorder=True, mt=15, m=0, style={'position': 'block', 'overflow': 'inherit'})
        return navbar

    def content_wrapper(self):
        """Create a layout of the main content"""
        return dmc.Grid([
                    dmc.Col(
                        dmc.MediaQuery(
                            dmc.Card(
                                self.filter_wrapper(),
                                mt=15,
                                mb=0,
                                withBorder=True,
                                radius='md',
                                h='100%',
                                style={'overflow': 'inherit'}),
                            largerThan='md',
                            innerBoxStyle={'width': '100%'},
                            styles={
                                'min-height': 'calc(100vh - 140px)',
                                'height': 'calc(100vh - 138px)'}
                        ),
                        p=8,
                        span=12,
                        id='grid-provider',
                        mb=0,
                        pb=0,
                        md=1.7),
                    dmc.Col(
                        dmc.MediaQuery(
                            dmc.ScrollArea(
                                self.dashboard_wrapper(),
                                mt=15,
                                h='100%',
                                w='100%'
                            ),
                            innerBoxStyle={'width': '100%'},
                            largerThan='md',
                            styles={'height': 'calc(100vh - 135px)'}),
                        span='auto')
                ])

    def render(self, app):
        container = dmc.Container(
            [
                self.navbar(app),
                self.content_wrapper()
            ], size='xxl')
        return container

    def app_shell_clientside(self, app):
        """Add additional callbacks on the client side"""
        # Hide filters
        app.clientside_callback(
            """ function(data) {  return data["display"]  } """,
            Output("grid-provider", "display"),
            Input("filter-wrapper-store", "data"),
        )
        app.clientside_callback(
            """function(n_clicks, sn_clicks1, data) {
                if (data) {
                    if (n_clicks || n_clicks1) {
                        const colsnum = data["display"] == "block" ? "none" : "block"
                        return { display: colsnum} 
                    }
                    return dash_clientside.no_update
                } else {
                    return { display: "block" }
                }
            }""",
            Output("filter-wrapper-store", "data"),
            Input("filter-wrapper-toggle", "n_clicks"),
            Input("filter-wrapper-dropdown", "n_clicks"),
            State("filter-wrapper-store", "data"),
        )
        
    def app_shell_serverside(self, app):
        """Add additional server-side callbacks"""
        ...

class AsideAppShell(BaseAppShell):
    def navbar(self, app):
        """Create a navigation panel layout"""
        navbar = dmc.Header(self.nav_content(app), height=60, m=0, p=10, style={'position': 'block', 'overflow': 'inherit'})
        return navbar
    
    def content_wrapper(self):
        """Create a layout of the main content"""
        return dmc.Grid([
                    dmc.Col(
                        dmc.MediaQuery(
                            dmc.ScrollArea(
                                self.dashboard_wrapper(),
                                mt=15,
                                h='100%',
                                w='100%'
                            ),
                            innerBoxStyle={'width': '100%'},
                            largerThan='md',
                            styles={'height': 'calc(100vh - 135px)'}),
                        span='auto')
                ])
    
    def render(self, app):
        container = dmc.Container(
            [
                self.navbar(app),
                self.content_wrapper()
            ], size=1500)
        navbar = dmc.Drawer(
                padding="md",
                # fixed=True,
                size=250,
                # opened=True,
                overlayOpacity=0.55,
                overlayBlur=3,
                zIndex=9,
                id='drawer',
                # height='calc(100vh-60px)',
                children=self.filter_wrapper(),
            )
        return html.Div([navbar, container])
    
    def app_shell_clientside(self, app):
       # Hide filters
        app.clientside_callback(
            """ function(n,n2, opened) {  
                if (n || n2) {return opened != true } 
                return dash_clientside.no_update} """,
            Output("drawer", "opened"),
            Input("filter-wrapper-toggle", "n_clicks"),
            Input("filter-wrapper-dropdown", "n_clicks"),
            State("drawer", "opened"),
        )