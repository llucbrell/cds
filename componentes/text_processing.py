from jinja2 import Template
from datetime import datetime

def render_template(template_text):
    # Datos dinámicos para la plantilla
    context = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S')
    }

    # Procesar la plantilla con Jinja2
    template = Template(template_text)
    rendered_text = template.render(context)

    return rendered_text
