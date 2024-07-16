from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

NAME = 'Bar Chart Plugin'

layout = html.Div([
    html.H2("Bar Chart"),
    dcc.Graph(id='bar-chart')
])

def update_data(app, execution_data, unique_id):
    @app.callback(
        Output(unique_id, 'figure'),
        [Input('execution-data', 'data')]
    )
    def update_chart(execution_data):
        if execution_data is None:
            return {}
        df = pd.DataFrame(execution_data)
        print("Data received in bar chart plugin:", df)
        fig = px.bar(df, x='id', y='duration', title='Duration by ID')
        return fig

def register_callbacks(app):
    print("Registering callbacks for Bar Chart Plugin")
    update_data(app, None, 'bar-chart')
