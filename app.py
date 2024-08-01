from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory, send_file, Response as FlaskResponse
from execution_analysis import create_dash_app
from models import Database, Values
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import base64
import io
import json
import os
from componentes.text_processing import process_text
from componentes.send_request import send_to_model
import threading
import time
import csv
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from models import Collection, Test, Response, Execution, Data, Values  # Ajusta la ruta de importación según sea necesario
from io import BytesIO  # Importar BytesIO para manejar datos binarios
from bs4 import BeautifulSoup
import requests
import logging
import jsonfinder





app = Flask(__name__)


# Crear una nueva fábrica de sesiones
DATABASE_URL = "sqlite:///tests.db"
engine = create_engine(DATABASE_URL)
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)


# Integrar Dash en Flask
dash_app = create_dash_app(app)

db = Database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Rutas para colecciones
@app.route('/collections', methods=['GET', 'POST'])
def collections():
    if request.method == 'POST':
        name = request.form['name']
        db.add_collection(name)
        return redirect(url_for('collections'))
    collections = db.get_collections()
    return render_template('collections.html', collections=collections)

@app.route('/update_collection/<int:collection_id>', methods=['POST'])
def update_collection(collection_id):
    try:
        data = request.json
        db.update_collection(
            collection_id,
            data.get('name'),
            model_name=data.get('model_name'),
            auth_url=data.get('auth_url'),
            api_key=data.get('api_key'),
            target_url=data.get('target_url'),
            request_template=data.get('request_template'),
            prompt_template=data.get('prompt_template')
        )
        return jsonify({'status': 'success', 'message': 'Collection updated successfully.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


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

@app.route('/tests/update_name/<int:test_id>', methods=['POST'])
def update_test_name(test_id):
    try:
        data = request.get_json()
        new_test_name = data.get('new_test_name')
        if not new_test_name:
            return jsonify({'status': 'error', 'message': 'El nombre del test no puede estar vacío.'})
        
        test = db.get_test(test_id)
        test.name = new_test_name
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Nombre del test actualizado con éxito.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

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

@app.route('/tests/config/<int:test_id>/<int:collection_id>', methods=['GET', 'POST'])
def config_test(test_id, collection_id):
    if request.method == 'POST':
        try:
            data = request.get_json()
            auth_url = data.get('auth-url-input')
            model_name = data.get('new-model-name-input')
            api_key = data.get('api-key-input')
            target_url = data.get('my-input')
            template_request = data.get('template-request')
            prompt_template = data.get('template-input')
            
            db.save_data(test_id, model_name=model_name, auth_url=auth_url, api_key=api_key, target_url=target_url, request_template=template_request, prompt_template=prompt_template)
            return jsonify({'message': 'Data saved successfully', 'status': 'success'})
        except Exception as e:
            return jsonify({'message': str(e), 'status': 'error'})

    collection = db.get_collection(collection_id)
    test = db.get_test(test_id)
    data = db.get_data(test_id)
    
    if data:
        model_name = data.model_name
        auth_url = data.auth_url
        api_key = data.api_key
        target_url = data.target_url
        template_request = data.request_template
        prompt_template = data.prompt_template
    else:
        model_name = auth_url = api_key = target_url = template_request = prompt_template = ''
    
    return render_template('config.html', 
                           collection_name=collection.name, 
                           test_name=test.name, 
                           model_name=model_name, 
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
        return jsonify({'message': f'{response}', 'status': 'success'})
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



# Ruta para visualizar las ejecuciones de un test
@app.route('/executions/<int:test_id>')
def executions(test_id):
    test = db.get_test(test_id)
    executions = db.get_executions(test_id)
    # Obtener las claves únicas de los items iterables
    iterable_values = db.session.query(Values).filter_by(test_id=test_id, value_type='iterable').all()
    iterable_keys = list(set([value.value_key for value in iterable_values]))
    return render_template('executions.html', test=test, executions=executions, iterable_keys=iterable_keys)

def run_execution(test_id, template_text, iterable_index=None):
    rendered_text = process_text(template_text, test_id, iterable_index)
    print(f"Execution result: {rendered_text}")
    # Aquí puedes añadir la lógica para ejecutar el test utilizando `rendered_text`
    db.add_execution(test_id, result=rendered_text)


def process_and_send(template_text, test_id, iterable_index=None):
    rendered_text = process_text(template_text, test_id, iterable_index)
    # Aquí puedes añadir la lógica para enviar la petición y recibir la respuesta
    data = db.get_data(test_id)
    url = data.target_url
    headers = {'Authorization': f'Bearer {data.api_key}'}

    start_time = time.time()
    response = requests.post(url, headers=headers, data=rendered_text)
    end_time = time.time()

    duration = end_time - start_time
    status_code = response.status_code
    response_text = response.text

    # Almacenar los resultados en la base de datos
    db.add_execution(test_id, result=response_text)

    execution = db.get_executions(test_id)[-1]
    execution.result = response_text
    #execution.timestamp = func.now()
    execution.duration = duration
    execution.status_code = status_code
    db.session.commit()

def launch_thread(rendered_template, async_option):
    # lanza un thread
    print("lanzando thread")

@app.route('/start-execution/<int:test_id>', methods=['POST'])
def start_execution(test_id):
    selected_key = request.form.get('key')
    selection_type = request.form.get('selection_type')
    async_option = request.form.get('async_option') == 'true'
    repetitions = request.form.get('repetitions')
    
    print("RECIBIDO")
    print(selection_type)
    print(selected_key)
    print(repetitions)
    print(async_option)
    
    session = Session()
    data = session.query(Data).filter_by(test_id=test_id).first()
    if not data or not data.prompt_template:
        session.close()
        raise ValueError("No data or prompt template found for the test")

    template_text = data.prompt_template
    print(template_text)

    request_template = data.request_template
    print(request_template)

    # Obtener el número de veces que la clave aparece en la base de datos
    key_count = session.query(Values).filter_by(test_id=test_id, value_key=selected_key, value_type='iterable').count()
    print(f"La clave '{selected_key}' aparece {key_count} veces en la base de datos.")

    if selection_type == 'iterable':
        repetitions = key_count
    else:
        repetitions = int(repetitions) if repetitions else 1

    if repetitions:
        key_count = repetitions        

    # Insert data into database
    new_execution = Execution(test_id=test_id, result="In Progress")
    session.add(new_execution)
    session.commit()
    execution_id = new_execution.id  # Obtener el ID de la nueva ejecución
    session.close()

    # Define the function to run in a thread
    def run_single_execution(iterable_index):
        session = Session()
        rendered_text = process_text(template_text, test_id, iterable_index)
        # Simulación de una solicitud de red y almacenamiento de resultados en la base de datos
        data = session.query(Data).filter_by(test_id=test_id).first()
        target_url = data.target_url
        model_name = data.model_name
        headers = {'Authorization': f'Bearer {data.api_key}'}
        
        print(rendered_text)
        start_time = time.time()
        response = send_process_template_to_model(rendered_text)
        end_time = time.time()
        print(response)
        
        duration = end_time - start_time
        db.add_response(execution_id=execution_id, response_data=response, start_time=start_time, end_time=end_time, duration=duration, model_name=model_name, target_url=target_url )
        #status_code = response.status_code
        #response_text = response.text
        
        # Actualizar la ejecución en la base de datos con los resultados
        execution = session.query(Execution).filter_by(id=execution_id).first()
        #execution.result = response_text
        #execution.timestamp = func.now()
        #execution.duration = duration
        #execution.status_code = status_code
        session.commit()
        session.close()
    
    def send_process_template_to_model(processed_text):
        ndata = db.get_data(test_id)
        print(ndata.target_url)
        print(ndata.auth_url)
        print(ndata.api_key)
        print(ndata.request_template)
        print(processed_text)
        resp = send_to_model(ndata.auth_url, ndata.api_key, ndata.target_url, processed_text, ndata.request_template)
        return resp

    def run_all_executions():
        for iterable_index in range(key_count):
            run_single_execution(iterable_index)
        if selection_type == 'iterable':
            update_execution_status(execution_id, f"Ended with {key_count} iterations of key {selected_key}")
        else:
            update_execution_status(execution_id, f"Ended with {key_count} iterative repetitions")

    def update_execution_status(execution_id, status):
        session = Session()
        execution = session.query(Execution).filter_by(id=execution_id).first()
        execution.result = status
        session.commit()
        session.close()

    if async_option:
        # Ejecutar un hilo por cada iteración
        threads = []
        for iterable_index in range(key_count):
            thread = threading.Thread(target=run_single_execution, args=(iterable_index,))
            threads.append(thread)
            thread.start()
        # Asegurarse de que todos los hilos hayan terminado antes de actualizar el estado
        for thread in threads:
            thread.join()
        update_execution_status(execution_id, "Ended")
    else:
        # Ejecutar el bucle en un nuevo hilo de manera síncrona
        thread = threading.Thread(target=run_all_executions)
        thread.start()

    return redirect(url_for('executions', test_id=test_id))

# Ruta para pausar una ejecución
@app.route('/pause-execution/<int:execution_id>', methods=['POST'])
def pause_execution(execution_id):
    execution = db.get_execution(execution_id)
    execution.result = "Paused"
    db.session.commit()
    return redirect(url_for('executions', test_id=execution.test_id))

# Ruta para borrar una ejecución
@app.route('/delete-execution/<int:execution_id>', methods=['POST'])
def delete_execution(execution_id):
    execution = db.get_execution(execution_id)
    test_id = execution.test_id
    db.session.delete(execution)
    db.session.commit()
    return redirect(url_for('executions', test_id=test_id))

@app.route('/execution-results/<int:execution_id>')
def execution_results(execution_id):
    execution = db.get_execution(execution_id)
    test_results = db.get_responses(execution_id)
    return render_template('executions_results.html', execution=execution, test_results=test_results)


@app.route('/get-executions/<int:test_id>', methods=['GET'])
def get_executions(test_id):
    session = Session()
    executions = session.query(Execution).filter_by(test_id=test_id).all()
    session.close()
    # Verificar las horas antes de formatearlas
    for execution in executions:
        print(f"ID: {execution.id}, Timestamp: {execution.timestamp}")
    return jsonify([{
        'id': execution.id,
        'result': execution.result,
        #'timestamp': execution.timestamp.strftime('%d-%m-%Y %H:%M')
        'timestamp': execution.timestamp.isoformat() 
    } for execution in executions])


##########################################################
# Ruta para la aplicación Dash a modo de manager de datos
##########################################################
"""""
@app.route('/tests/config/<int:test_id>/<int:collection_id>')
def config_test(test_id, collection_id):
    # Pasar el contenido HTML generado por Dash al renderizar la plantilla
    return render_template('dash_layout.html', dash_html=dash_app.index(), test_id=test_id, collection_id=collection_id)

"""

@app.route('/execution_analysis/<int:execution_id>/')
def execution_analysis(execution_id):
    # Pasar el contenido HTML generado por Dash al renderizar la plantilla
    return render_template('dash_layout.html', dash_html=dash_app.index(), execution_id=execution_id)


@app.route('/download_csv/<int:execution_id>')
def download_csv(execution_id):
    # Aquí deberías escribir lógica para generar el archivo CSV y devolverlo como una descarga
    # Por ejemplo:
    # filename = f'execution_{execution_id}.csv'
    # Generar el archivo CSV y guardarlo temporalmente o devolverlo directamente con send_file
    # return send_file(filename, as_attachment=True)
    return "Placeholder para la descarga de CSV"


@app.route('/download_all_data_csv', methods=['GET'])
def download_all_data_csv():
    columns = request.args.getlist('columns')
    
    # Obtener todos los datos de ejecuciones y respuestas
    session = Session()
    executions = session.query(Execution).all()
    responses = session.query(Response).all()
    
    # Crear archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Escribir encabezados basados en las columnas seleccionadas
    headers = []
    if 'ID' in columns:
        headers.append('ID')
    if 'Test ID' in columns:
        headers.append('Test ID')
    if 'Timestamp' in columns:
        headers.append('Timestamp')
    if 'Resultado' in columns:
        headers.append('Resultado')
    if 'Datos de Respuesta' in columns:
        headers.append('Datos de Respuesta')
    if 'Hora de Inicio' in columns:
        headers.append('Hora de Inicio')
    if 'Hora de Finalización' in columns:
        headers.append('Hora de Finalización')
    if 'Duración' in columns:
        headers.append('Duración')
    if 'Fecha' in columns:
        headers.append('Fecha')
    if 'Modelo' in columns:
        headers.append('Modelo')
    if 'Url Destino' in columns:
        headers.append('Url Destino')
    
    writer.writerow(headers)
    
    # Escribir datos de ejecuciones y respuestas
    for execution in executions:
        execution_data = []

        if 'ID' in columns:
            execution_data.append(execution.id)  # Asegurar que la columna se omite si no está seleccionada
        if 'Test ID' in columns:
           execution_data.append(execution.test_id)  # Asegurar que la columna se omite si no está seleccionada
        if 'Timestamp' in columns:
            execution_data.append(execution.timestamp)  # Asegurar que la columna se omite si no está seleccionada
        if 'Resultado' in columns:
            execution_data.append(execution.result)  # Asegurar que la columna se omite si no está seleccionada
            # Añade más campos según sea necesario

    for response in responses:
        response_data = []

        if 'Datos de Respuesta' in columns:
            response_data.append(response.response_data)  # Asegurar que la columna se omite si no está seleccionada
        if 'Hora de Inicio' in columns:
            response_data.append(response.start_time)  # Asegurar que la columna se omite si no está seleccionada
        if 'Hora de Finalización' in columns:
            response_data.append(response.end_time)  # Asegurar que la columna se omite si no está seleccionada
        if 'Duración' in columns:
            response_data.append(response.duration)  # Asegurar que la columna se omite si no está seleccionada
        if 'Fecha' in columns:
            response_data.append(response.date)  # Asegurar que la columna se omite si no está seleccionada
        if 'Modelo' in columns:
            response_data.append(response.model_name)  # Asegurar que la columna se omite si no está seleccionada
        if 'Url Destino' in columns:
            response_data.append(response.target_url)  # Asegurar que la columna se omite si no está seleccionada
            # Añade más campos según sea necesario
        writer.writerow(execution_data + response_data)
    
    # Convertir StringIO a BytesIO
    output.seek(0)
    output_binary = BytesIO(output.read().encode('utf-8'))
    
    # Volver al principio del archivo CSV y devolverlo como una descarga
    output_binary.seek(0)
    return send_file(
        output_binary,
        mimetype='text/csv',
        as_attachment=True,
        download_name='data.csv'
    )



@app.route('/download_data_csv', methods=['GET'])
def download_data_csv():
    columns = request.args.getlist('columns')
    execution_id = request.args.get('execution_id')

    # Validar el execution_id
    if not execution_id or not execution_id.isdigit():
        return "ID de ejecución inválido", 400

    execution_id = int(execution_id)

    # Obtener datos de ejecuciones y respuestas
    session = Session()
    executions = session.query(Execution).filter(Execution.id == execution_id).all()
    responses = session.query(Response).filter(Response.execution_id == execution_id).all()

    # Crear archivo CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)

    # Escribir encabezados basados en las columnas seleccionadas
    headers = []
    if 'ID' in columns:
        headers.append('ID')
    if 'Test ID' in columns:
        headers.append('Test ID')
    if 'Timestamp' in columns:
        headers.append('Timestamp')
    if 'Resultado' in columns:
        headers.append('Resultado')
    if 'Datos de Respuesta' in columns:
        headers.append('Datos de Respuesta')
    if 'Hora de Inicio' in columns:
        headers.append('Hora de Inicio')
    if 'Hora de Finalización' in columns:
        headers.append('Hora de Finalización')
    if 'Duración' in columns:
        headers.append('Duración')
    if 'Fecha' in columns:
        headers.append('Fecha')
    if 'Modelo' in columns:
        headers.append('Modelo')
    if 'Url Destino' in columns:
        headers.append('Url Destino')

    writer.writerow(headers)
    # Escribir datos de ejecuciones y respuestas
    for execution in executions:
        execution_data = []

        if 'ID' in columns:
            execution_data.append(execution.id)  # Asegurar que la columna se omite si no está seleccionada
        if 'Test ID' in columns:
           execution_data.append(execution.test_id)  # Asegurar que la columna se omite si no está seleccionada
        if 'Timestamp' in columns:
            execution_data.append(execution.timestamp)  # Asegurar que la columna se omite si no está seleccionada
        if 'Resultado' in columns:
            execution_data.append(execution.result)  # Asegurar que la columna se omite si no está seleccionada
            # Añade más campos según sea necesario

    for response in responses:
        response_data = []

        if 'Datos de Respuesta' in columns:
            response_data.append(response.response_data)  # Asegurar que la columna se omite si no está seleccionada
        if 'Hora de Inicio' in columns:
            response_data.append(response.start_time)  # Asegurar que la columna se omite si no está seleccionada
        if 'Hora de Finalización' in columns:
            response_data.append(response.end_time)  # Asegurar que la columna se omite si no está seleccionada
        if 'Duración' in columns:
            response_data.append(response.duration)  # Asegurar que la columna se omite si no está seleccionada
        if 'Fecha' in columns:
            response_data.append(response.date)  # Asegurar que la columna se omite si no está seleccionada
        if 'Modelo' in columns:
            response_data.append(response.model_name)  # Asegurar que la columna se omite si no está seleccionada
        if 'Url Destino' in columns:
            response_data.append(response.target_url)  # Asegurar que la columna se omite si no está seleccionada
            # Añade más campos según sea necesario
        writer.writerow(execution_data + response_data)
 
    # Convertir StringIO a BytesIO
    output.seek(0)
    output_binary = BytesIO(output.read().encode('utf-8'))

    # Volver al principio del archivo CSV y devolverlo como una descarga
    output_binary.seek(0)
    return send_file(
        output_binary,
        mimetype='text/csv',
        as_attachment=True,
        download_name='data.csv'
    )

@app.route('/download_multiple_txt/<int:execution_id>')
def download_multiple_txt(execution_id):
    # Aquí deberías escribir lógica para generar múltiples archivos TXT y devolverlos como una descarga ZIP
    # Por ejemplo:
    # Generar los archivos TXT y guardarlos en un archivo ZIP temporal
    # return send_file('archivo_zip_temporal.zip', as_attachment=True)
    return "Placeholder para la descarga de múltiples TXT"

@app.route('/results_executions_all', methods=['GET'])
def all_executions():
    session = Session()
    executions = session.query(Execution).all()
    responses = session.query(Response).all()

    test_id = 1  # Ejemplo, obtén el test_id según tu lógica

    return render_template('executions_results_all.html', executions=executions, responses=responses, test_id=test_id)

@app.route('/get_collection/<int:collection_id>', methods=['GET'])
def get_collection(collection_id):
    session = Session()
    collection = session.query(Collection).filter(Collection.id == collection_id).first()
    if collection:
        return jsonify({
            'status': 'success',
            'data': {
                'name': collection.name,
                'model_name': collection.model_name,
                'auth_url': collection.auth_url,
                'api_key': collection.api_key,
                'target_url': collection.target_url,
                'request_template': collection.request_template,
                'prompt_template': collection.prompt_template
            }
        })
    else:
        return jsonify({'status': 'error', 'message': 'Collection not found'}), 404



@app.route('/scraping', methods=['GET', 'POST'])
def scraping():
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        levels = int(request.form['levels'])
        db.add_scraping_config(name, url, levels)
        return redirect(url_for('scraping'))
    
    configs = db.get_scraping_configs()
    return render_template('scraping.html', configs=configs)

@app.route('/scraping/<int:config_id>', methods=['GET', 'POST'])
def edit_scraping(config_id):
    config = db.get_scraping_config(config_id)
    if request.method == 'POST':
        name = request.form['name']
        url = request.form['url']
        levels = int(request.form['levels'])
        config.name = name
        config.url = url
        config.levels = levels
        db.session.commit()
        return redirect(url_for('scraping'))
    
    return render_template('edit_scraping.html', config=config)

@app.route('/scraping/delete/<int:config_id>')
def delete_scraping(config_id):
    db.delete_scraping_config(config_id)
    return redirect(url_for('scraping'))


@app.route('/scrape/<int:config_id>')
def scrape(config_id):
    config = db.get_scraping_config(config_id)
    url = config.url
    levels = config.levels
    result_text = perform_scraping(url, levels)
    db.add_scraping_result(config_id, result_text)
    return render_template('scraping_result.html', config=config, result_text=result_text)

@app.route('/scrape_json/<int:config_id>')
def scrape_json(config_id):
    config = db.get_scraping_config(config_id)
    url = config.url
    levels = config.levels
    
    # Realizar el scraping normal
    scraped_text = perform_scraping(url, levels)
    
    # Extraer JSON del texto resultante
    json_data = extract_json_from_text(scraped_text)
    
    return jsonify(json_data)

@app.route('/scrape_xml/<int:config_id>')
def scrape_xml(config_id):
    config = db.get_scraping_config(config_id)
    url = config.url
    levels = config.levels
    xml_data = perform_scraping_xml(url, levels)
    return FlaskResponse(xml_data, mimetype='application/xml')

@app.route('/scrape_csv/<int:config_id>')
def scrape_csv(config_id):
    config = db.get_scraping_config(config_id)
    url = config.url
    levels = config.levels
    csv_data = perform_scraping_csv(url, levels)
    return FlaskResponse(csv_data, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=scraped_data.csv'})



# Configurar el logger
""""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def perform_scraping(url, levels):
    visited_urls = set()
    result_texts = []

    def scrape_page(current_url, current_level):
        if current_level > levels or current_url in visited_urls:
            return
        visited_urls.add(current_url)
        
        logger.info(f'Visiting: {current_url} (Level {current_level})')
        
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Eliminar CSS y JavaScript
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        
        text = ' '.join(soup.stripped_strings)
        result_texts.append(text)

        if current_level < levels:
            for link in soup.find_all('a', href=True):
                next_url = link['href']
                if not next_url.startswith('http'):
                    next_url = requests.compat.urljoin(current_url, next_url)
                scrape_page(next_url, current_level + 1)

    scrape_page(url, 1)
    return '\n\n'.join(result_texts)



def extract_json_from_text(text):
    json_data = []
    for start, end, obj in jsonfinder.jsonfinder(text):
        if obj is not None:
            json_data.append(obj)
    return json_data



def perform_scraping_xml(url, levels):
    visited_urls = set()
    xml_data = []

    def scrape_page(current_url, current_level):
        if current_level > levels or current_url in visited_urls:
            return
        visited_urls.add(current_url)
        
        logger.info(f'Visiting: {current_url} (Level {current_level})')
        
        response = requests.get(current_url)
        content_type = response.headers['Content-Type'].lower()
        if 'application/xml' in content_type or 'text/xml' in content_type:
            xml_data.append(response.text)

        if current_level < levels:
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                next_url = link['href']
                if not next_url.startswith('http'):
                    next_url = requests.compat.urljoin(current_url, next_url)
                scrape_page(next_url, current_level + 1)

    scrape_page(url, 1)
    return '\n\n'.join(xml_data)

def perform_scraping_csv(url, levels):
    visited_urls = set()
    data_frames = []

    def scrape_page(current_url, current_level):
        if current_level > levels or current_url in visited_urls:
            return
        visited_urls.add(current_url)
        
        logger.info(f'Visiting: {current_url} (Level {current_level})')
        
        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        for table in tables:
            df = pd.read_html(str(table))[0]
            data_frames.append(df)

        if current_level < levels:
            for link in soup.find_all('a', href=True):
                next_url = link['href']
                if not next_url.startswith('http'):
                    next_url = requests.compat.urljoin(current_url, next_url)
                scrape_page(next_url, current_level + 1)

    scrape_page(url, 1)
    if data_frames:
        combined_df = pd.concat(data_frames, ignore_index=True)
        csv_data = combined_df.to_csv(index=False)
        return csv_data
    else:
        return ""
"""


if __name__ == '__main__':
    app.run(debug=True)
