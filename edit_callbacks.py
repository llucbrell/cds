from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from dash.dependencies import ALL
import dash_bootstrap_components as dbc
from app import app  # Asegúrate de que `app` se ha definido antes de este import

@app.callback(
    [Output("test-warning", "children"),
     Output("test-table", "children"),
     Output("alert", "message")],
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

    if "add-test-button" in triggered_id and add_n_clicks:
        if test_name:
            # Aquí puedes agregar la lógica para interactuar con la base de datos.
            return warning_message, [], "Botón Agregar Test presionado"
        else:
            warning_message = "El nombre del test no puede estar vacío."
    
    if "delete-test-button" in triggered_id:
        delete_index = ctx.triggered[0]['prop_id'].split('.')[0]
        test_id = eval(delete_index)["index"]
        # Aquí puedes agregar la lógica para eliminar de la base de datos.
        warning_message = f"Botón Borrar Test con ID {test_id} presionado"

    return warning_message, [], ""

