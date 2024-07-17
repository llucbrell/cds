from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import nltk

nltk.download('punkt')

NAME = 'Token Count Mean Bar Chart Plugin'

layout = html.Div([
    html.H2("Token Count Mean Bar Chart"),
    dcc.Graph(id='token-count-bar-chart')
])

def count_tokens(text):
    words = nltk.word_tokenize(text)
    return len(words)

def update_data(app, execution_data, unique_id_bar_chart):
    @app.callback(
        Output(unique_id_bar_chart, 'figure'),
        [Input('execution-data', 'data')]
    )
    def update_chart(execution_data):
        if execution_data is None:
            return {}
        
        df = pd.DataFrame(execution_data)
        df['token_count'] = df['response_data'].apply(count_tokens)
        
        print("Data received in token count plugin:", df)

        # Create the bar chart for mean token count by ID
        mean_token_count = df.groupby('id')['token_count'].mean().reset_index()
        bar_fig = px.bar(mean_token_count, x='id', y='token_count', title='Mean Token Count by ID')
        
        # Calculate the overall mean token count
        overall_mean = df['token_count'].mean()
        
        # Add a horizontal line for the overall mean token count
        bar_fig.add_shape(
            type='line',
            x0=mean_token_count['id'].min(),
            x1=mean_token_count['id'].max(),
            y0=overall_mean,
            y1=overall_mean,
            line=dict(color='Red', dash='dash'),
        )

        # Add annotation for the overall mean line
        bar_fig.add_annotation(
            text=f'Overall Mean: {overall_mean:.2f}',
            xref='paper',
            x=1,
            y=overall_mean,
            yref='y',
            showarrow=False,
            align='right',
            font=dict(color='Red')
        )

        return bar_fig

def register_callbacks(app):
    print("Registering callbacks for Token Count Plugin")
    update_data(app, 'execution-data', 'token-count-bar-chart')
