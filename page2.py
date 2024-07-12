import dash
import dash_html_components as html

def create_page2(app):
    layout = html.Div([
        html.H1('Página 2'),
        html.P('Esta es la segunda página.')
    ])
    return layout
