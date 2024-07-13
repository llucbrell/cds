from dash import dcc, html
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import json

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        html.H1(id='collection-name', className="text-left my-4"),
        html.H1(id='test-name', className="text-center my-4"),
    ]),
    dbc.Row([
        html.H1("Datos Generales", className="text-center my-4"),
        dbc.Col([
            html.H3('Auth URL', className="my-4"),
            dcc.Input(id='auth-url-input', placeholder='http://example.com/api/v1/auth', value="", type='text', className="form-control"),
            dbc.Button('Save', id='save-auth-url-button', color='primary', className="mt-2"),
            html.Div(id='save-auth-url-output', className="mt-2"),
            html.H3('API Key', className="my-4"),
            dcc.Input(id='api-key-input', placeholder='Your API Key', value="", type='text', className="form-control"),
            dbc.Button('Save', id='save-api-key-button', color='primary', className="mt-2"),
            html.Div(id='save-api-key-output', className="mt-2"),
            html.H3('Destination URL', className="my-4"),
            dcc.Input(id='my-input', placeholder='http://example.com', value="", type='text', className="form-control"),
            dbc.Button('Save', id='save-target-url-button', color='primary', className="mt-2"),
            html.Div(id='save-target-url-output', className="mt-2"),
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3('Plantilla de Request', className="form-label"),
            dcc.Textarea(id='template-request', placeholder="Escribe la plantilla de request como objeto json, sustitución dinámica de {{url}}, {{payload}}, {{api_key}} y {{prompt}} por sus respectivos valores." ,value='', className="form-control", style={'width': '100%', 'height': 200}),
            dbc.Button('Save', id='save-request-template', color='primary', className="mt-2"),
            # dbc.Button('Process Template', id='template-request-button', color='primary', className="mt-2"),
            html.Div(id='template-request-output', className="mt-3"),
            dcc.Store(id='processed-text-request-store')
        ])
    ]),
    dbc.Row([
        
        html.H1("Administrador de datos", className="text-center my-4"),
            dcc.Tabs(id='tabs', children=[
                dcc.Tab(label='Ítems Fijos', children=[
                    html.Div([
                        html.H4('Crear Ítem Fijo'),
                        dbc.Input(id='fixed-key', placeholder='Clave'),
                        dbc.Input(id='fixed-value', placeholder='Valor'),
                        dbc.Button('Agregar Ítem Fijo', id='add-fixed', color='primary', className="mt-2"),
                        html.Div(id='fixed-output', className="mt-3")
                    ]),
                    html.Div(id='fixed-items', className="mt-3")
                ]),
                dcc.Tab(label='Ítems Iterables', children=[
                    html.Div([
                        html.H4('Crear Ítem Iterable'),
                        dcc.Upload(id='upload-iterable', children=html.Button('Subir CSV')),
                        dbc.Input(id='iterable-range', placeholder='Rango (ej. A-C)'),
                        dbc.Button('Agregar Ítem Iterable', id='add-iterable', color='primary', className="mt-2"),
                        html.Div(id='iterable-output', className="mt-3")
                    ]),
                    html.Div(id='iterable-items', className="mt-3")
                ]),
                dcc.Tab(label='Ítems Arrays', children=[
                    html.Div([
                        html.H4('Crear Ítem Array'),
                        dcc.Upload(id='upload-array', children=html.Button('Subir CSV')),
                        dbc.Button('Agregar Ítem Array', id='add-array', color='primary', className="mt-2"),
                        html.Div(id='array-output', className="mt-3")
                    ]),
                    html.Div(id='array-items', className="mt-3")
                ])
            ])
    ]),
    
    dbc.Row([
        html.H1("Combinar Prompt", className="text-center my-4"),
        dbc.Col([
            html.H3('Constructor de plantilla de Prompts', className="form-label"),
            dcc.Textarea(id='template-input', placeholder="Escribe combinando texto normal y texto entre {{}} de manera que se sustituyan los valores al pulsar sobre el botón, prueba con {{date}}" ,value='', className="form-control", style={'width': '100%', 'height': 200}),
            dbc.Button('Save', id='save-prompt-template', color='primary', className="mt-2"),
            dbc.Button('Process Template', id='template-button', color='primary', className="mt-2"),
            dbc.Button('Prueba', id='template-send-button', color='primary', className="mt-2", disabled=False),
            html.Div(id='template-output', className="mt-3"),
            html.Div(id='save-prompt-template-output', className="mt-3"),
            dcc.Store(id='processed-text-store')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='send-output', className="mt-3")
        ])
    ])
], fluid=True)
