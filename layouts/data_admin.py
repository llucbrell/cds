from dash import dcc, html

layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Input(id='my-input', value='initial value', type='text'),
    html.Div(id='my-output'),
    html.Button('Click Me', id='my-button'),
    html.Div(id='button-output'),
    html.Div(id='collection-name'),
    html.Div(id='test-name')
])
