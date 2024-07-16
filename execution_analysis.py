from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State, ALL
import dash_bootstrap_components as dbc
import importlib
import os
import pandas as pd
from models import Database
import uuid

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True
    )

    dash_app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.H1("Aplicación Dash con Plugins"),
        dcc.Store(id='execution-data'),
        html.Div(id='plugin-list')
    ])

    db = Database()

    def register_plugins():
        plugins = []
        plugins_dir = 'plugins'
        for filename in os.listdir(plugins_dir):
            if filename.endswith('.py') and filename != '__init__.py':
                plugin_name = filename[:-3]
                module = importlib.import_module(f'{plugins_dir}.{plugin_name}')
                plugins.append({'label': module.NAME, 'value': plugin_name})
                if hasattr(module, 'register_callbacks'):
                    module.register_callbacks(dash_app)
        return plugins

    plugins = register_plugins()

    @dash_app.callback(
        Output('plugin-list', 'children'),
        Input('plugin-list', 'children')
    )
    def display_plugin_list(_):
        return [html.Div([
                    dcc.Checklist(
                        options=[{'label': plugin['label'], 'value': plugin['value']}],
                        id={'type': 'plugin-checkbox', 'index': plugin['value']},
                        inputStyle={"margin-right": "10px"},
                        labelStyle={"font-size": "20px"}
                    ),
                    html.Div(id={'type': 'plugin-container', 'index': plugin['value']})
                ], className='plugin-checkbox-container') for plugin in plugins]

    @dash_app.callback(
        Output('execution-data', 'data'),
        Input('url', 'pathname')
    )
    def load_execution_data(pathname):
        try:
            parts = pathname.strip('/').split('/')
            if len(parts) < 2 or not parts[-1].isdigit():
                print(f"Invalid pathname for execution_id: {pathname}")
                return []
            
            execution_id = int(parts[-1])
            responses = db.get_responses(execution_id)
            df = pd.DataFrame([response.to_dict() for response in responses])
            print("Loaded execution data:", df)
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading execution data: {e}")
            return []

    @dash_app.callback(
        Output({'type': 'plugin-container', 'index': ALL}, 'children'),
        [Input({'type': 'plugin-checkbox', 'index': ALL}, 'value')],
        State('execution-data', 'data')
    )
    def display_plugin(selected_plugins, execution_data):
        content = [[] for _ in selected_plugins]
        for i, selected in enumerate(selected_plugins):
            if selected:
                module = importlib.import_module(f'plugins.{plugins[i]["value"]}')
                plugin_layout = module.layout
                unique_id = str(uuid.uuid4())
                plugin_layout.id = unique_id  # Assign a unique ID
                content[i].append(plugin_layout)
                if hasattr(module, 'update_data'):
                    module.update_data(dash_app, execution_data, unique_id)
        return content

    return dash_app
