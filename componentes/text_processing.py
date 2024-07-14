from jinja2 import Template
from datetime import datetime
from models import Database, Values

def process_text(template_text, test_id, iterable_index=None):
    # Inicializar base de datos
    db = Database()
    
    # Datos dinámicos para la plantilla
    context = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'time': datetime.now().strftime('%H:%M:%S')
    }

    # Obtener valores fijos y de tipo array del test específico
    fixed_values = db.session.query(Values).filter_by(test_id=test_id, value_type='fixed').all()
    array_values = db.session.query(Values).filter_by(test_id=test_id, value_type='array').all()
    iterable_values = db.session.query(Values).filter_by(test_id=test_id, value_type='iterable', iterable_index=iterable_index).all()


    # Añadir valores fijos al contexto
    for value in fixed_values:
        context[value.value_key] = value.value_value

    # Añadir valores de tipo array al contexto
    for value in array_values:
        if value.value_key not in context:
            context[value.value_key] = []
        # Dividir el valor almacenado por comas para crear una lista
        context[value.value_key].extend(value.value_value.split(','))

    # Añadir valores de tipo iterable al contexto si se proporciona un índice
    if iterable_index is not None:
        for value in iterable_values:
            context[value.value_key] = value.value_value

    # Procesar la plantilla con Jinja2
    template = Template(template_text)
    rendered_text = template.render(context)

    return rendered_text

