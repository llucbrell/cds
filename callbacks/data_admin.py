from dash.dependencies import Input, Output, State
from models import Database
from componentes.text_processing import render_template
from componentes.send_request import send_to_model
import dash

def register_callbacks(dash_app):
    db = Database()

    @dash_app.callback(
        Output('auth-url-input', 'value'),
        Output('api-key-input', 'value'),
        Output('my-input', 'value'),
        Output('template-input', 'value'),
        Input('url', 'pathname')
    )
    def load_data(pathname):
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            data = db.get_data(test_id)
            if data:
                return data.auth_url, data.api_key, data.target_url, data.prompt_template
        return '', '', '', ''

    @dash_app.callback(
        Output('save-auth-url-output', 'children'),
        [Input('save-auth-url-button', 'n_clicks')],
        [State('auth-url-input', 'value'), State('url', 'pathname')]
    )
    def save_auth_url(n_clicks, auth_url, pathname):
        if n_clicks is None:
            return ''
        
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            db.save_data(test_id, auth_url=auth_url)
            return 'Auth URL saved'

    @dash_app.callback(
        Output('save-api-key-output', 'children'),
        [Input('save-api-key-button', 'n_clicks')],
        [State('api-key-input', 'value'), State('url', 'pathname')]
    )
    def save_api_key(n_clicks, api_key, pathname):
        if n_clicks is None:
            return ''
        
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            db.save_data(test_id, api_key=api_key)
            return 'API Key saved'

    @dash_app.callback(
        Output('save-target-url-output', 'children'),
        [Input('save-target-url-button', 'n_clicks')],
        [State('my-input', 'value'), State('url', 'pathname')]
    )
    def save_target_url(n_clicks, target_url, pathname):
        if n_clicks is None:
            return ''
        
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            db.save_data(test_id, target_url=target_url)
            return 'Target URL saved'

    @dash_app.callback(
        Output('save-prompt-template-output', 'children'),
        [Input('save-prompt-template', 'n_clicks')],
        [State('template-input', 'value'), State('url', 'pathname')]
    )
    def save_prompt_template(n_clicks, template_text, pathname):
        if n_clicks is None:
            return ''
        
        parts = pathname.strip('/').split('/')
        if len(parts) >= 4 and parts[0] == 'tests' and parts[1] == 'config':
            test_id = int(parts[2])
            db.save_data(test_id, prompt_template=template_text)
            return 'Prompt Template saved'

    @dash_app.callback(
        Output('processed-text-store', 'data'),
        Output('template-output', 'children'),
        [Input('template-button', 'n_clicks')],
        [State('template-input', 'value')]
    )
    def process_template(n_clicks, template_text):
        if n_clicks is None or template_text is None:
            return '', ''
        
        rendered_text = render_template(template_text)
        return rendered_text, rendered_text

    @dash_app.callback(
        Output('send-output', 'children'),
        Output('template-send-button', 'disabled'),
        [Input('template-send-button', 'n_clicks')],
        [State('auth-url-input', 'value'), State('api-key-input', 'value'), State('my-input', 'value'), State('processed-text-store', 'data')]
    )
    def send_processed_template(n_clicks, auth_url, api_key, url, processed_text):
        if n_clicks is None or not auth_url or not api_key or not url or not processed_text:
            return 'Invalid Auth URL, API Key, URL, or processed text', False

        try:
            response = send_to_model(auth_url, api_key, url, processed_text)
            return f'Sent to {url}. Response: {response}', False
        except Exception as e:
            return str(e), False
