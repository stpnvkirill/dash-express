import dash_mantine_components as dmc

from dash import html
from .filterfunc import select_filters, multiselect_filters, range_filters,dateselect_filters, daterange_filters


MT = 27

def create_label(label, col):
    return dmc.Text(col.capitalize() if label == 'auto' else label, weight='bold')

def create_slidersingle(serias, col, mt=None, **kwargs):
    return dmc.Card(dmc.Slider(
        id=dict(type='filter', id=col),
        labelAlwaysOn=True,
        min=serias.round().min(),
        max=serias.round().max(),
        value=round(serias.mean()),
        mt=MT,
        **kwargs), withBorder=True)

def create_rangeslider(serias, col, mt=None, **kwargs):
    return dmc.Card(dmc.RangeSlider(
        id=dict(type='filter', id=col),
        labelAlwaysOn=True,
        min=serias.round().min(),
        max=serias.round().max(),
        mt=MT,
        **kwargs), withBorder=True)

def create_slider(serias, col, multi, label=None, **kwargs):
    dct_func = {True:create_rangeslider, False:create_slidersingle}
    dct_filter_func = {True:range_filters, False:select_filters}
    return dct_filter_func.get(multi), html.Div([create_label(label, col), dct_func.get(multi)(serias, col, **kwargs)])

def create_selectsingle(serias, col, placeholder='Select value', **kwargs):
    return dmc.Select(
        id=dict(type='filter', id=col),
        placeholder=placeholder,
        data=[{'label': str(s), 'value': s} for s in serias.unique()],
        **kwargs)

def create_multiselect(serias, col, placeholder='Select value', **kwargs):
    return dmc.MultiSelect(
        id=dict(type='filter', id=col),
        placeholder=placeholder,
        data=[{'label': str(s), 'value': s} for s in serias.unique()],
        **kwargs)

def create_select(serias, col, multi, label=None, **kwargs):
    dct_func = {True:create_multiselect, False:create_selectsingle}
    dct_filter_func = {True:multiselect_filters, False:select_filters}
    return dct_filter_func.get(multi), html.Div([create_label(label, col),dct_func.get(multi)(serias, col, **kwargs)])

def create_datesingle(serias, col, placeholder='Select date', **kwargs):
    return dmc.DatePicker(
        id=dict(type='filter', id=col),
        placeholder=placeholder,
        value=serias.mean().floor('d').date(),
        minDate=serias.dt.floor('d').min(),
        maxDate=serias.dt.floor('d').max(),
        **kwargs)

def create_daterange(serias, col, placeholder='Select date',  clearable=True, **kwargs):
    return dmc.DateRangePicker(
        id=dict(type='filter', id=col),
        clearable=False,
        placeholder=placeholder,
        value=[serias.min().floor('d').date(), serias.max().floor('d').date()],
        minDate=serias.dt.floor('d').min(),
            maxDate=serias.dt.floor('d').max(),
            **kwargs)

def create_date(serias, col, multi, label=None, **kwargs):
    dct_func = {True:create_daterange, False:create_datesingle}
    dct_filter_func = {True:daterange_filters, False:dateselect_filters}
    return dct_filter_func.get(multi), html.Div([create_label(label, col),dct_func.get(multi)(serias, col, **kwargs)])


def autofilter(type,serias, col, multi,
        persistence=True, **kwargs):
    dct_func = {'select':create_select, 'slider':create_slider, 'datepicker':create_date}
    return dct_func.get(type)(serias, col, multi, 
        persistence=persistence, **kwargs)