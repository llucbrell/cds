import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
from database import Database
from layout import create_layout

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
db = Database()

app.layout = create_layout

@app.callback(
    [Output("collection-warning", "children"),
     Output("collection-table", "children")],
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
        delete_index = ctx.triggered[0]['prop_id'].split('.')[0]
        collection_id = eval(delete_index)["index"]
        db.delete_collection(collection_id)

    collections = db.get_collections()
    rows = []
    for collection in collections:
        row = html.Tr([
            html.Td(collection.name),
            html.Td(collection.id),
            html.Td([
                dbc.Button("Editar", href=f"/edit/{collection.id}", size="sm", className="ml-2"),
                dbc.Button("Borrar", id={"type": "delete-collection-button", "index": collection.id}, size="sm", className="ml-2")
            ])
        ])
        rows.append(row)

    return warning_message, [dbc.Table([
        html.Thead(html.Tr([html.Th("Nombre"), html.Th("ID"), html.Th("Acciones")])),
        html.Tbody(rows)
    ], bordered=True, striped=True, hover=True)]

if __name__ == '__main__':
    app.run_server(debug=True)
