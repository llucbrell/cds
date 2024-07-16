from dash import dcc, html
from dash.dependencies import Input, Output

NAME = 'Mi Plugin'

layout = html.Div([
    html.H2("Gráfico del Plugin"),
    dcc.Graph(id='my-graph'),
    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0)
])

def register_callbacks(app):
    @app.callback(
        Output('my-graph', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def update_graph(n):
        # Lógica para actualizar el gráfico
        return {
            'data': [{'x': [1, 2, 3], 'y': [n, n*2, n*3], 'type': 'line'}],
            'layout': {'title': 'Gráfico Actualizado'}
        }
