from dash import dcc, html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    dbc.Row([
        html.H1(id='collection-name', className="text-left my-4"),
        html.H1(id='test-name', className="text-center my-4"),
    ]),
    dbc.Row([
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
            dcc.Textarea(id='template-request', placeholder="Escribe la plantilla de reques como objeto json" ,value='', className="form-control", style={'width': '100%', 'height': 200}),
            dbc.Button('Save', id='save-request-template', color='primary', className="mt-2"),
            dbc.Button('Download', id='download-request-template', color='primary', className="mt-2"),
            dbc.Button('Load', id='load-request-template', color='primary', className="mt-2"),
            dbc.Button('Process Template', id='template-request-button', color='primary', className="mt-2"),
            html.Div(id='template-request-output', className="mt-3"),
            dcc.Store(id='processed-text-request-store')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3('Constructor de plantilla de Prompts', className="form-label"),
            dcc.Textarea(id='template-input', placeholder="Escribe combinando texto normal y texto entre {{}} de manera que se sustituyan los valores al pulsar sobre el botón, prueba con {{date}}" ,value='', className="form-control", style={'width': '100%', 'height': 200}),
            dbc.Button('Save', id='save-prompt-template', color='primary', className="mt-2"),
            dbc.Button('Download', id='download-prompt-template', color='primary', className="mt-2"),
            dbc.Button('Load', id='load-prompt-template', color='primary', className="mt-2"),
            dbc.Button('Process Template', id='template-button', color='primary', className="mt-2"),
            dbc.Button('Prueba', id='template-send-button', color='primary', className="mt-2", disabled=False),
            html.Div(id='template-output', className="mt-3"),
            dcc.Store(id='processed-text-store')
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.Div(id='send-output', className="mt-3")
        ])
    ])
], fluid=True)
