from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd

NAME = 'Responses Plugin'

layout = html.Div([
    html.H2("Responses Data"),
    #dash_table.DataTable(data=df.to_dict('records'), page_size=10)
    dash_table.DataTable(
        id='responses-table',
        columns=[{"name": i, "id": i} for i in ["id", "execution_id", "response_data", "start_time", "end_time", "duration", "date"]],
        data=[],
        page_size=15,
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
