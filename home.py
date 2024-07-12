import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output

def create_home_page(app):
    layout = html.Div([
        html.H1('Página Principal'),
        dcc.Link(html.Button('Ver'), href='/page2')
    ])
    return layout
