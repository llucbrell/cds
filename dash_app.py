from dash import Dash, dcc, html
from dash.dependencies import Input, Output

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
    )

    dash_app.layout = html.Div([
        dcc.Input(id='my-input', value='initial value', type='text'),
        html.Div(id='my-output'),
        html.Button('Click Me', id='my-button'),
        html.Div(id='button-output')
    ])

    @dash_app.callback(
        Output(component_id='my-output', component_property='children'),
        [Input(component_id='my-input', component_property='value')]
    )
    def update_output_div(input_value):
        return f'Output: {input_value}'

    @dash_app.callback(
        Output(component_id='button-output', component_property='children'),
        [Input(component_id='my-button', component_property='n_clicks')]
    )
    def update_button_output(n_clicks):
        if n_clicks is None:
            return 'Button not clicked yet'
        else:
            return f'Button clicked {n_clicks} times'

    return dash_app
