from dash import Dash
from layouts.data_admin import layout
#from callbacks.data_admin import register_callbacks
import dash_bootstrap_components as dbc

def create_dash_app(flask_app):
    dash_app = Dash(
        __name__,
        server=flask_app,
        url_base_pathname='/dash/',
        external_stylesheets=[dbc.themes.BOOTSTRAP]  # Utiliza el tema de Bootstrap
    )
    
    # Asigna el layout
    #dash_app.layout = layout
    
    # Registra los callbacks
    #register_callbacks(dash_app)
    
    return dash_app
