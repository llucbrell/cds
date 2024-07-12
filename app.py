import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
from database import Database

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
db = Database()

app.layout = html.Div([
    dbc.Container([
        html.H1("Gestión de Colecciones de Tests"),
        html.Hr(),
        dbc.Row([
            dbc.Col([
                html.H3("Colecciones"),
                dbc.Input(id="new-collection-name", placeholder="Nombre de la colección", type="text", className="mb-2"),
                dbc.Button("Agregar Colección +", id="add-collection-button", color="primary", className="mb-2"),
                html.Div(id="collection-warning", style={"color": "red"}),
                html.Ul(id="collection-list")
            ])
        ])
    ])
])

@app.callback(
    [Output("collection-warning", "children"),
     Output("collection-list", "children")],
    [Input("add-collection-button", "n_clicks"),
     Input({"type": "delete-collection-button", "index": ALL}, "n_clicks")],
    [State("new-collection-name", "value"),
     State({"type": "delete-collection-button", "index": ALL}, "id")]
)
def manage_collections(add_n_clicks, delete_n_clicks, collection_name, delete_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    warning_message = ""
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if "add-collection-button" in triggered_id and add_n_clicks:
        if collection_name:
            existing_collections = db.get_collections()
            if any(collection.name == collection_name for collection in existing_collections):
                warning_message = "La colección ya existe."
            else:
                db.add_collection(collection_name)

    if "delete-collection-button" in triggered_id:
        # Obtener el índice del id del botón de eliminación que se activó
        delete_index = ctx.triggered[0]['prop_id'].split('.')[0]
        collection_id = eval(delete_index)["index"]
        db.delete_collection(collection_id)

    collections = db.get_collections()
    collection_items = [html.Li([
        html.Span(f"{collection.name} (ID: {collection.id})"),
        dbc.Button("Editar", id={"type": "edit-collection-button", "index": collection.id}, size="sm", className="ml-2"),
        dbc.Button("Borrar", id={"type": "delete-collection-button", "index": collection.id}, size="sm", className="ml-2")
    ]) for collection in collections]

    return warning_message, collection_items

if __name__ == '__main__':
    app.run_server(debug=True)
