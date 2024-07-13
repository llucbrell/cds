from dash.dependencies import Input, Output, State
from models import Database
from componentes.text_processing import render_template
from componentes.send_request import send_to_model
import dash
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import base64
import io
import pandas as pd

def register_item_callbacks(app):
    db = Database()

    @app.callback(
        Output('fixed-output', 'children'),
        Output('fixed-items', 'children'),
        Input('add-fixed', 'n_clicks'),
        State('fixed-key', 'value'),
        State('fixed-value', 'value')
    )
    def update_fixed_items(n_clicks, key, value):
        if n_clicks:
            db.add_value(test_id=1, value_key=key, value_value=value, value_type='fixed')  # Reemplaza 'test_id=1' con el id adecuado
            output_message = 'Ítem fijo agregado'
        else:
            output_message = ''
        
        values = db.get_values(test_id=1)  # Reemplaza 'test_id=1' con el id adecuado
        fixed_values = [v for v in values if v.value_type == 'fixed']
        fixed_items = html.Ul([html.Li(f"{v.value_key}: {v.value_value}") for v in fixed_values])
        
        return output_message, fixed_items

    @app.callback(
        Output('iterable-output', 'children'),
        Output('iterable-items', 'children'),
        Input('add-iterable', 'n_clicks'),
        State('upload-iterable', 'contents'),
        State('iterable-range', 'value')
    )
    def update_iterable_items(n_clicks, contents, range_str):
        if n_clicks and contents and range_str:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            start, end = map(int, range_str.split('-'))
            for i in range(start, end + 1):
                row = df.iloc[i]
                db.add_value(test_id=1, value_key=row['key'], value_value=row['value'], value_type='iterable', iterable_index=i)  # Reemplaza 'test_id=1' con el id adecuado
            output_message = 'Ítem iterable agregado'
        else:
            output_message = ''
        
        values = db.get_values(test_id=1)  # Reemplaza 'test_id=1' con el id adecuado
        iterable_values = [v for v in values if v.value_type == 'iterable']
        iterable_items = html.Ul([html.Li(f"Index {v.iterable_index} - {v.value_key}: {v.value_value}") for v in iterable_values])
        
        return output_message, iterable_items

    @app.callback(
        Output('array-output', 'children'),
        Output('array-items', 'children'),
        Input('add-array', 'n_clicks'),
        State('upload-array', 'contents')
    )
    def update_array_items(n_clicks, contents):
        if n_clicks and contents:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            array_str = df.to_json(orient='records')
            db.add_value(test_id=1, value_key='array', value_value=array_str, value_type='array')  # Reemplaza 'test_id=1' con el id adecuado
            output_message = 'Ítem array agregado'
        else:
            output_message = ''
        
        values = db.get_values(test_id=1)  # Reemplaza 'test_id=1' con el id adecuado
        array_values = [v for v in values if v.value_type == 'array']
        array_items = html.Ul([html.Li(v.value_value) for v in array_values])
        
        return output_message, array_items