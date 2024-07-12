from flask import Flask, render_template, request, redirect, url_for
from dash_app import create_dash_app
from models import Database

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
    return render_template('tests.html', tests=tests, collection=collection)

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




#################################
# Ruta para la aplicación Dash
@app.route('/dash')
def render_dash():
    # Pasar el contenido HTML generado por Dash al renderizar la plantilla
    return render_template('dash_layout.html', dash_html=dash_app.index())

if __name__ == '__main__':
    app.run(debug=True)
