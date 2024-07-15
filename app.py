from flask import Flask, render_template, request, redirect, url_for, jsonify
from dash_app import create_dash_app
from models import Database, Values
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
import threading
import time
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from models import Collection, Test, Execution, Data, Values  # Ajusta la ruta de importación según sea necesario

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
        url = data.target_url
        headers = {'Authorization': f'Bearer {data.api_key}'}
        
        print(rendered_text)
        start_time = time.time()
        #response = requests.post(url, headers=headers, data=rendered_text)
        send_process_template_to_model(rendered_text)
        end_time = time.time()
        
        duration = end_time - start_time
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
        
        
        response = send_to_model(ndata.auth_url, ndata.api_key, ndata.target_url, processed_text, ndata.request_template)
        print(response)

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

# Ruta para ver los resultados de una ejecución
@app.route('/execution-results/<int:execution_id>')
def execution_results(execution_id):
    execution = db.get_execution(execution_id)
    return render_template('execution_results.html', execution=execution)


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

if __name__ == '__main__':
    app.run(debug=True)
