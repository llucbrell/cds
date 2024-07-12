from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output
import dash_html_components as html
import dash_core_components as dcc
from home import create_home_page
from page2 import create_page2

server = Flask(__name__)
app = Dash(__name__, server=server, url_base_pathname='/')

# Configurar el layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback para actualizar la página
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page2':
        return create_page2(app)
    else:
        return create_home_page(app)

if __name__ == '__main__':
    app.run_server(debug=True)
