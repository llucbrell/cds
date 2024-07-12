import dash_bootstrap_components as dbc
from dash import html, dcc

def create_edit_page(collection_id):
    return html.Div([
        dcc.Store(id='collection-id', data=collection_id),
        html.H1(f"Editar Colección: {collection_id}"),
        dcc.Link("Volver a la página principal", href="/"),
        dbc.Input(id="new-collection-name", placeholder="Nombre de la colección", type="text", className="mb-2"),
        dbc.Row([
            dbc.Col([
                html.H3("Tests"),
                dbc.Input(id="new-test-name", placeholder="Nombre del test", type="text", className="mb-2"),
                dbc.Button("Agregar Test +", id="add-test-button", color="primary", className="mb-2"),
                html.Div(id="test-warning", style={"color": "red"}),
                html.Div(id="test-table")
            ])
        ]),
        # Aquí puedes agregar más componentes para editar la colección
    ])
