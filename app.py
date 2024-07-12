from flask import Flask, render_template
from dash_app import create_dash_app

app = Flask(__name__)

# Integrar Dash en Flask
dash_app = create_dash_app(app)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la aplicación Dash
@app.route('/dash')
def render_dash():
    # Pasar el contenido HTML generado por Dash al renderizar la plantilla
    return render_template('dash_layout.html', dash_html=dash_app.index())

if __name__ == '__main__':
    app.run(debug=True)
