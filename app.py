from dash_express import DashExpress, Page, dmc
from pages import create_home_page, create_expos_page, create_ddu_page, create_v_page


app = DashExpress(title='HyperDash', 
                eager_loading=True,
                update_title=None,#'Загрузка...',
                )

app.LOGO = {'type':'str', 'children':'DashExpress'}

# Pages
app.regester_page(create_home_page(app))
app.regester_page(create_ddu_page(app))
app.regester_page(create_expos_page(app))
app.regester_page(create_v_page(app))


app.run(debug=True)
