import dash_bootstrap_components as dbc
from dash import dcc, html

create_layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.Container([
        html.H1("Gestión de Colecciones de Tests"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H3("Colecciones"),
                dbc.Input(id="new-collection-name", placeholder="Nombre de la colección", type="text", className="mb-2"),
                dbc.Button("Agregar Colección +", id="add-collection-button", color="primary", className="mb-2"),
                html.Div(id="collection-warning", style={"color": "red"}),
                html.Div(id="collection-table")
            ])
        ])
    ])
])
