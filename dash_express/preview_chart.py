import random
import plotly.graph_objects as go

from dash import Patch


def bubble(df):
    n = random.randint(5, 35)
    x = [random.randint(1,96) for i in range(n)]
    y = [random.randint(85000,178957) for i in range(n)]
    fig = go.Figure(data=[go.Scatter(
        x=x, y=y,
        text=['A<br>size: 40', 'B<br>size: 60',
                'C<br>size: 80', 'D<br>size: 100'],
        mode='markers',
        marker=dict(
            color=['rgb(93, 164, 214)', 'rgb(255, 144, 14)',
                    'rgb(44, 160, 101)', 'rgb(255, 65, 54)'],
            size=[40, 60, 80, 100],
        )
    )])
    fig.update_layout(showlegend=False)
    return fig
    
def pie(df):
    labels = ['Oxygen','Hydrogen','Carbon_Dioxide','Nitrogen']
    values = [random.randint(19,596) for i in range(4)]

    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, sort=True)])
    fig.update_layout(showlegend=False)
    return fig

def line(df):
    # Add data
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December']
    high_2000 = [random.randint(100,800)/10 for i in range(len(month))]
    low_2000 = [random.randint(100,800)/10 for i in range(len(month))]
    high_2007 = [random.randint(100,800)/10 for i in range(len(month))]
    low_2007 = [random.randint(100,800)/10 for i in range(len(month))]
    high_2014 = [random.randint(100,800)/10 for i in range(len(month))]
    low_2014 = [random.randint(100,800)/10 for i in range(len(month))]
    w = 2
    data = {
        'High 2014':{'y':high_2014,  'line':dict(color='firebrick', width=w)},
        'Low 2014': {'y':low_2014, 'line':dict(color='royalblue', width=w)},
        'High 2007':{'y':high_2007, 'line':dict(color='firebrick', width=w,
                              dash='dash')},
        'Low 2007':{'y':low_2007, 'line':dict(color='royalblue', width=w, dash='dash')},
        'High 2000':{'y':high_2000, 'line':dict(color='firebrick', width=w, dash='dot')},
        'Low 2000':{'y':low_2000, 'line':dict(color='royalblue', width=w, dash='dot')}

    }

    fig = go.Figure()
    # Create and style traces
    for name, kwargs in data.items():
        fig.add_trace(go.Scatter(x=month, name=name, **kwargs))
    return fig
    
def _render_wrapper():
    return random.choice([bubble, pie, line])
