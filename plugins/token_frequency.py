from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from nltk.tokenize import RegexpTokenizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
from io import BytesIO

NAME = 'Word Frequency Word Cloud Plugin'

layout = html.Div([
    html.H2("Word Frequency Word Cloud"),
    html.Img(id='word-frequency-wordcloud')
])

def count_tokens(text):
    tokenizer = RegexpTokenizer(r'\w+')
    words = tokenizer.tokenize(text.lower())  # Convertir a minúsculas para contar todas las palabras iguales
    return words

def update_data(app, execution_data, unique_id_wordcloud):
    @app.callback(
        Output(unique_id_wordcloud, 'src'),
        [Input('execution-data', 'data')]
    )
    def update_wordcloud(execution_data):
        if execution_data is None:
            return ''

        # Concatenar todas las respuestas
        all_responses = " ".join([item['response_data'] for item in execution_data])
        words = count_tokens(all_responses)

        # Contar la frecuencia de cada palabra
        word_counts = pd.Series(words).value_counts().to_dict()

        # Crear la nube de palabras
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_counts)

        # Convertir la nube de palabras a una imagen en formato base64
        img = BytesIO()
        wordcloud.to_image().save(img, format='PNG')
        img.seek(0)
        img_base64 = base64.b64encode(img.read()).decode('utf-8')

        return 'data:image/png;base64,{}'.format(img_base64)

def register_callbacks(app):
    print("Registering callbacks for Word Frequency Word Cloud Plugin")
    update_data(app, 'execution-data', 'word-frequency-wordcloud')

