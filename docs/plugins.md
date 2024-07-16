# Plugin Development Documentation for Dash Application

This documentation provides guidelines on how to create plugins for the Dash application. Plugins can dynamically update based on data loaded from a database without needing to restart the server. Follow these steps to create and integrate a new plugin.

## Plugin Structure

Each plugin should be a Python module located in the `plugins` directory. The module should contain:
- A `NAME` variable defining the name of the plugin.
- A `layout` variable defining the Dash layout for the plugin.
- An `update_data` function to handle data updates.
- A `register_callbacks` function to register the plugin's callbacks with the main Dash app.

### Example Plugin: Responses Table

Create a file named `responses_table.py` in the `plugins` directory with the following content:

```python
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

NAME = 'Responses Plugin'

layout = html.Div([
    html.H2("Responses Data"),
    dash_table.DataTable(
        id='responses-table',
        columns=[{"name": i, "id": i} for i in ["id", "execution_id", "response_data", "start_time", "end_time", "duration", "date"]],
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left', 'padding': '5px'},
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold'
        },
    )
])

def update_data(app, execution_data, unique_id):
    @app.callback(
        Output(unique_id, 'data'),
        [Input('execution-data', 'data')]
    )
    def update_table(execution_data):
        if execution_data is None:
            return []
        df = pd.DataFrame(execution_data)
        print("Data received in plugin:", df)
        return df.to_dict('records')

def register_callbacks(app):
    print("Registering callbacks for Responses Plugin")
    update_data(app, None, 'responses-table')
