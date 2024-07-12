from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate  # Asegúrate de importar PreventUpdate
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
from app import app, db  # Asegúrate de que `app` y `db` se han definido antes de este import

@app.callback(
    [Output("test-warning", "children"),
     Output("test-table", "children")],
    [Input("add-test-button", "n_clicks"),
     Input({"type": "delete-test-button", "index": ALL}, "n_clicks")],
    [State("new-test-name", "value"),
     State("collection-id", "data"),
     State({"type": "delete-test-button", "index": ALL}, "id")]
)
def manage_tests(add_n_clicks, delete_n_clicks, test_name, collection_id, delete_ids):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise PreventUpdate

    warning_message = ""
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    print(f"Triggered ID: {triggered_id}")
    print(f"add_n_clicks: {add_n_clicks}, delete_n_clicks: {delete_n_clicks}")
    print(f"test_name: {test_name}, collection_id: {collection_id}, delete_ids: {delete_ids}")

    if "add-test-button" in triggered_id and add_n_clicks:
        if test_name:
            db.add_test(collection_id, test_name)
        else:
            warning_message = "El nombre del test no puede estar vacío."

    if "delete-test-button" in triggered_id:
        delete_index = ctx.triggered[0]['prop_id'].split('.')[0]
        test_id = eval(delete_index)["index"]
        db.delete_test(test_id)

    tests = db.get_tests(collection_id)
    rows = []
    for test in tests:
        row = html.Tr([
            html.Td(test.name),
            html.Td(test.id),
            html.Td([
                dbc.Button("Borrar", id={"type": "delete-test-button", "index": test.id}, size="sm", className="ml-2")
            ])
        ])
        rows.append(row)

    return warning_message, [dbc.Table([
        html.Thead(html.Tr([html.Th("Nombre"), html.Th("ID"), html.Th("Acciones")])),
        html.Tbody(rows)
    ], bordered=True, striped=True, hover=True)]
