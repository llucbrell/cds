from flask import Flask, render_template, request, redirect, url_for, jsonify
from dash_app import create_dash_app
from models import Database
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import json
from componentes.text_processing import process_text
from componentes.send_request import send_to_model

app = Flask(__name__)

# Integrar Dash en Flask
dash_app = create_dash_app(app)

db = Database()

@app.route('/')
def index():
    return render_template('index.html')

# Rutas para colecciones
@app.route('/collections', methods=['GET', 'POST'])
def collections():
    if request.method == 'POST':
        name = request.form['name']
        db.add_collection(name)
        return redirect(url_for('collections'))
    collections = db.get_collections()
    return render_template('collections.html', collections=collections)

@app.route('/collections/edit/<int:collection_id>', methods=['GET', 'POST'])
def edit_collection(collection_id):
    collection = db.get_collection(collection_id)
    if request.method == 'POST':
        new_name = request.form['name']
        db.update_collection(collection_id, new_name)
        return redirect(url_for('collections'))
    return render_template('edit_collection.html', collection=collection)

@app.route('/collections/delete/<int:collection_id>')
def delete_collection(collection_id):
    db.delete_collection(collection_id)
    return redirect(url_for('collections'))

# Rutas para tests
@app.route('/tests/<int:collection_id>', methods=['GET', 'POST'])
def tests(collection_id):
    collection = db.get_collection(collection_id)
    if request.method == 'POST':
        name = request.form['name']
        db.add_test(collection_id, name)
        return redirect(url_for('tests', collection_id=collection_id))
    tests = db.get_tests(collection_id)
    return render_template('tests.html', tests=tests, collection=collection, collection_id=collection_id)

@app.route('/tests/delete/<int:test_id>/<int:collection_id>')
def delete_test(test_id, collection_id):
    db.delete_test(test_id)
    return redirect(url_for('tests', collection_id=collection_id))

# Rutas para ejecuciones
@app.route('/executions/<int:test_id>', methods=['GET', 'POST'])
def executions(test_id):
    if request.method == 'POST':
        result = request.form['result']
        db.add_execution(test_id, result)
        return redirect(url_for('executions', test_id=test_id))
    executions = db.get_executions(test_id)
    return render_template('executions.html', executions=executions, test_id=test_id)

@app.route('/executions/delete/<int:execution_id>/<int:test_id>')
def delete_execution(execution_id, test_id):
    db.delete_execution(execution_id)
    return redirect(url_for('executions', test_id=test_id))

@app.route('/tests/config/<int:test_id>/<int:collection_id>', methods=['GET', 'POST'])
def config_test(test_id, collection_id):
    if request.method == 'POST':
        try:
            data = request.get_json()
            auth_url = data.get('auth-url-input')
            api_key = data.get('api-key-input')
            target_url = data.get('my-input')
            template_request = data.get('template-request')
            prompt_template = data.get('template-input')
            
            db.save_data(test_id, auth_url=auth_url, api_key=api_key, target_url=target_url, request_template=template_request, prompt_template=prompt_template)
            return jsonify({'message': 'Data saved successfully', 'status': 'success'})
        except Exception as e:
            return jsonify({'message': str(e), 'status': 'error'})

    collection = db.get_collection(collection_id)
    test = db.get_test(test_id)
    data = db.get_data(test_id)
    
    if data:
        auth_url = data.auth_url
        api_key = data.api_key
        target_url = data.target_url
        template_request = data.request_template
        prompt_template = data.prompt_template
    else:
        auth_url = api_key = target_url = template_request = prompt_template = ''
    
    return render_template('config.html', 
                           collection_name=collection.name, 
                           test_name=test.name, 
                           auth_url=auth_url, 
                           api_key=api_key, 
                           target_url=target_url, 
                           template_request=template_request, 
                           prompt_template=prompt_template)


@app.route('/process-template', methods=['POST'])
def process_template():
    try:
        data = request.get_json()
        template_text = data.get('template-input')
        test_id = data.get('test-id')
        iterable_index = data.get('iterable-index')
        print(iterable_index)
        
        if not template_text or not test_id:
            raise ValueError("Template input and test ID are required")

        if not iterable_index:
            rendered_text = process_text(template_text, test_id)
        else:
            rendered_text = process_text(template_text, test_id, iterable_index)

        return jsonify({'rendered_text': rendered_text})
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'})



@app.route('/send-template', methods=['POST'])
def send_template():
    try:
        data = request.get_json()
        auth_url = data.get('auth-url-input')
        api_key = data.get('api-key-input')
        url = data.get('my-input')
        processed_text = data.get('processed-text')
        template_request_text = data.get('template-request')
        
        response = send_to_model(auth_url, api_key, url, processed_text, template_request_text)
        return jsonify({'message': f'Sent to {url}. Response: {response}', 'status': 'success'})
    except Exception as e:
        return jsonify({'message': str(e), 'status': 'error'})

# Rutas para gestionar valores
@app.route('/values/<int:test_id>', methods=['GET', 'POST'])
def values(test_id):
    if request.method == 'POST':
        data = request.json
        key = data.get('key')
        value = data.get('value')
        value_type = data.get('value_type')
        db.add_value(test_id, key, value, value_type)
        values = db.get_values(test_id)
        return jsonify({'status': 'success', 'message': 'Value added successfully', 'values': [v.to_dict() for v in values]})
    elif request.method == 'GET':
        values = db.get_values(test_id)
        return jsonify({'values': [v.to_dict() for v in values]})

@app.route('/values/edit/<int:value_id>', methods=['GET', 'POST'])
def edit_value(value_id):
    value = db.get_value(value_id)
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            key = data.get('key')
            value_value = data.get('value')
            value_type = data.get('value_type')
        else:
            key = request.form['key']
            value_value = request.form['value']
            value_type = request.form['value_type']
        db.update_value(value_id, key, value_value, value_type)
        return jsonify({'status': 'success', 'message': 'Value updated successfully'})
    return render_template('edit_value.html', value=value)

@app.route('/values/delete/<int:value_id>', methods=['POST'])
def delete_value(value_id):
    value = db.get_value(value_id)
    test_id = value.test_id
    db.delete_value(value_id)
    values = db.get_values(test_id)
    return jsonify({'status': 'success', 'message': 'Value deleted successfully', 'values': [{'id': v.id, 'key': v.value_key, 'value': v.value_value, 'value_type': v.value_type} for v in values]})


@app.route('/upload_csv', methods=['POST'])
def upload_csv():
    if 'csv_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'})

    file = request.files['csv_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'})

    try:
        df = pd.read_csv(file)
        csv_data = df.to_csv(index=False)
        return jsonify({'status': 'success', 'csv_data': csv_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/update_range', methods=['POST'])
def update_range():
    data = request.json
    range_start = data.get('range_start')
    range_end = data.get('range_end')
    
    # Dummy data, replace with your data frame or session stored data
    df = pd.read_csv('your_csv_file.csv') 

    try:
        range_df = df.loc[range_start:range_end]
        csv_data = range_df.to_csv(index=False)
        return jsonify({'status': 'success', 'csv_data': csv_data})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@app.route('/save_selection', methods=['POST'])
def save_selection():
    data = request.json
    print(data)
    test_id = data.get('test_id')
    value_key = data.get('value_key')
    value_value = data.get('value_value')
    string_array = ", ".join(map(str, value_value))
    print(string_array)
    print(value_key)
    print(test_id)
    
    if test_id and value_key and string_array:
        db = Database()
        db.add_value(test_id, value_key, string_array, value_type='array')
        return jsonify({'status': 'success', 'message': 'Data saved successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Not enought data received'})

@app.route('/save_iterable_selection', methods=['POST'])
def save_iterable_selection():
    data = request.json
    print(data)
    test_id = data.get('test_id')
    value_key = data.get('value_key')
    value_values = data.get('value_value')
    print(value_key)
    print(test_id)

    if test_id and value_key and value_values:
        db = Database()
        for index, item in enumerate(value_values):
            db.add_iterable_value(test_id, value_key, item, 'iterable', index)

        return jsonify({'status': 'success', 'message': 'Data saved successfully'})
    else:
        return jsonify({'status': 'error', 'message': 'Not enough data received'})


@app.route('/delete_iterable_values', methods=['POST'])
def delete_iterable_values():
    data = request.json
    test_id = data.get('test_id')
    value_key = data.get('value_key')
    
    if test_id and value_key:
        db = Database()
        num_deleted = db.delete_iterable_values_by_key(test_id, value_key)
        if num_deleted > 0:
            return jsonify({'status': 'success', 'message': f'{num_deleted} values deleted successfully'})
        else:
            return jsonify({'status': 'error', 'message': 'No values found to delete'})
    else:
        return jsonify({'status': 'error', 'message': 'test_id and value_key required'})

##########################################################
# Ruta para la aplicación Dash a modo de manager de datos
##########################################################
"""""
@app.route('/tests/config/<int:test_id>/<int:collection_id>')
def config_test(test_id, collection_id):
    # Pasar el contenido HTML generado por Dash al renderizar la plantilla
    return render_template('dash_layout.html', dash_html=dash_app.index(), test_id=test_id, collection_id=collection_id)

"""

if __name__ == '__main__':
    app.run(debug=True)
