from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import importlib
import os
import pandas as pd
from models import Database

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
        html.Div(id='plugin-list'),
        html.Div(id='plugin-content')
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
                    )
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
        Output('plugin-content', 'children'),
        [Input({'type': 'plugin-checkbox', 'index': plugin['value']}, 'value') for plugin in plugins],
        State('execution-data', 'data')
    )
    def display_plugin(*selected_plugins, execution_data=None):
        content = []
        for i, selected in enumerate(selected_plugins):
            if selected:
                try:
                    module = importlib.import_module(f'plugins.{plugins[i]["value"]}')
                    content.append(module.layout)
                    if hasattr(module, 'update_data'):
                        module.update_data(dash_app, execution_data)
                except IndexError:
                    print(f"Error: Index {i} out of range for plugins list.")
        return content

    return dash_app
