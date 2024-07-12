from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from models import Database

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/',
    )

    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
        dcc.Input(id='my-input', value='initial value', type='text'),
        html.Div(id='my-output'),
        html.Button('Click Me', id='my-button'),
        html.Div(id='button-output'),
        html.Div(id='collection-name'),
        html.Div(id='test-name')
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

    @dash_app.callback(
        Output(component_id='collection-name', component_property='children'),
        Output(component_id='test-name', component_property='children'),
        Input('url', 'pathname')
    )
    def update_collection_and_test_name(pathname):
        # Extrae el test_id y collection_id de la URL
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            collection_id = int(parts[3])
            db = Database()
            collection = db.get_collection(collection_id)
            test = db.get_test(test_id)
            if collection and test:
                return collection.name, test.name
        return 'N/A', 'N/A'

    return dash_app
