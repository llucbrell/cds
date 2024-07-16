from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import importlib
import os

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    dash_app.layout = html.Div([
        html.H1("Aplicación Dash con Plugins"),
        html.Div(id='plugin-list'),
        html.Div(id='plugin-content')
    ])

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
                        inputStyle={"margin-right": "10px"},  # Añadir margen al checkbox
                        labelStyle={"font-size": "20px"}  # Ajustar el tamaño del texto
                    )
                ], className='plugin-checkbox-container') for plugin in plugins]

    @dash_app.callback(
        Output('plugin-content', 'children'),
        [Input({'type': 'plugin-checkbox', 'index': plugin['value']}, 'value') for plugin in plugins]
    )
    def display_plugin(*selected_plugins):
        content = []
        for i, selected in enumerate(selected_plugins):
            if selected:
                module = importlib.import_module(f'plugins.{plugins[i]["value"]}')
                content.append(module.layout)
        return content

    return dash_app
