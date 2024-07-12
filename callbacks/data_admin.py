from dash.dependencies import Input, Output, State
from models import Database
from componentes.text_processing import render_template
from componentes.send_request import send_to_model

def register_callbacks(dash_app):
    @dash_app.callback(
        Output('my-output', 'children'),
        [Input('my-input', 'value')]
    )
    def update_output_div(input_value):
        return f'Output: {input_value}'

    @dash_app.callback(
        Output('button-output', 'children'),
        [Input('my-button', 'n_clicks')]
    )
    def update_button_output(n_clicks):
        if n_clicks is None:
            return 'Button not clicked yet'
        else:
            return f'Button clicked {n_clicks} times'

    @dash_app.callback(
        Output('collection-name', 'children'),
        Output('test-name', 'children'),
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

    @dash_app.callback(
        Output('processed-text-store', 'data'),
        Output('template-output', 'children'),
        [Input('template-button', 'n_clicks')],
        [State('template-input', 'value')]
    )
    def process_template(n_clicks, template_text):
        if n_clicks is None or template_text is None:
            return '', ''
        
        # Usar la función render_template para procesar el texto
        rendered_text = render_template(template_text)
        return rendered_text, rendered_text

    @dash_app.callback(
        Output('send-output', 'children'),
        [Input('template-send-button', 'n_clicks')],
        [State('my-input', 'value'), State('processed-text-store', 'data')]
    )
    def send_processed_template(n_clicks, url, processed_text):
        if n_clicks is None or not url or not processed_text:
            return 'Invalid URL or processed text'
        
        response = send_to_model(url, processed_text)
        return f'Sent to {url}. Response: {response}'
