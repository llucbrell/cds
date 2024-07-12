import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
from dash.exceptions import PreventUpdate
from database import Database

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
db = Database()

app.layout = html.Div([
    dbc.Container([
        html.H1("Editar Colección"),
        dcc.Location(id='url', refresh=False),
        html.Div(id="edit-content"),
    ])
])

@app.callback(
    Output("edit-content", "children"),
    [Input("url", "pathname")]
)
def display_edit_page(pathname):
    if not pathname.startswith("/edit/"):
        raise PreventUpdate

    collection_id = pathname.split("/")[-1]
    collection = db.get_collection(int(collection_id))

    if collection:
        return html.Div([
            html.H3(f"Editando colección: {collection.name} (ID: {collection.id})"),
            dbc.Input(id="edit-collection-name", value=collection.name, placeholder="Nuevo nombre de la colección", type="text", className="mb-2"),
            dbc.Button("Guardar Cambios", id="save-edit-button", color="primary", className="mb-2"),
            html.Div(id="edit-warning", style={"color": "red"})
        ])
    else:
        return html.Div([
            html.H3("Colección no encontrada."),
            dcc.Link("Volver a la página principal", href="/")
        ])

@app.callback(
    Output("edit-warning", "children"),
    Input("save-edit-button", "n_clicks"),
    [State("edit-collection-name", "value"),
     State("url", "pathname")]
)
def save_edit(n_clicks, new_name, pathname):
    if not n_clicks:
        raise PreventUpdate

    collection_id = pathname.split("/")[-1]
    if new_name:
        db.update_collection(int(collection_id), new_name)
        return "Cambios guardados con éxito."
    else:
        return "El nombre no puede estar vacío."

if __name__ == '__main__':
    app.run_server(debug=True)
