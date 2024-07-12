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
            html.H3('Url de destino', className="my-4"),
            dcc.Input(id='my-input', placeholder='http://example.com', value="", type='text', className="form-control"),
            html.Div(id='my-output', className="mt-3"),  # Asegurarnos de que existe
            html.Div(id='button-output', className="mt-3")  # Añadir el componente que falta
        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H3('Constructor de plantilla de Prompts', className="form-label"),
            dcc.Textarea(id='template-input', placeholder="Escribe combinando texto normal y texto entre {{}} de manera que se sustituyan los valores al pulsar sobre el botón, prueba con {{date}}" ,value='', className="form-control", style={'width': '100%', 'height': 200}),
            dbc.Button('Process Template', id='template-button', color='primary', className="mt-3"),
            dbc.Button('Prueba', id='template-send-button', color='primary', className="mt-3"),
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
