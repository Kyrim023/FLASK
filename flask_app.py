from flask import Flask, request, redirect
import os
import sys
import django

# Cargar libreriap
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prueba.settings')
django.setup()

from app_inventario.models import inventario, marca, categoria, estado
from app_inventario.libreriap import BASES, MODELOS, cargar_todos, concatenar_todos

app = Flask(__name__)

HTML_HEADER = """
<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">
<title>CRUD Flask</title>
<style>
    body { font-family: Arial; padding: 20px; background: #f5f5f5; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    th, td { padding: 10px; border: 1px solid #ccc; text-align: center; }
    th { background: #333; color: white; }
    form { margin-bottom: 20px; }
    input[type="text"] { width: 100%; padding: 8px; margin: 4px 0; }
    input[type="submit"], button { padding: 8px 16px; margin: 5px 0; }
    a { color: blue; text-decoration: none; margin-right: 10px; }
</style>
</head><body>
<h1>CRUD FLASK</h1>
<a href="/inventario">Inventario</a> | <a href="/marca">Marca</a> | <a href="/categoria">Categoría</a> | <a href="/estado">Estado</a><hr>
"""

HTML_FOOTER = "</body></html>"

def render_form(fields, action, values=None):
    values = values or {}
    form = f'<form method="post" action="{action}">'
    for field in fields:
        value = values.get(field, '')
        form += f'<label>{field.capitalize()}:</label><br><input type="text" name="{field}" value="{value}" required><br>'
    form += '<input type="submit" value="Guardar"></form><a href="javascript:history.back()">Volver</a>'
    return form

# Cargar y concatenar datos al iniciar para tener DataFrames combinados
datos_por_modelo = cargar_todos()
datos_concatenados = concatenar_todos(datos_por_modelo)

def recargar_datos():
    global datos_por_modelo, datos_concatenados
    datos_por_modelo = cargar_todos()
    datos_concatenados = concatenar_todos(datos_por_modelo)

def create_item(model_class, data):
    for db_alias in BASES:
        model_class.objects.using(db_alias).create(**data)
    recargar_datos()

def update_item(model_class, item_id, data):
    for db_alias in BASES:
        try:
            item = model_class.objects.using(db_alias).get(id=item_id)
            for k, v in data.items():
                setattr(item, k, v)
            item.save(using=db_alias)
        except model_class.DoesNotExist:
            pass
    recargar_datos()

def delete_item(model_class, item_id):
    for db_alias in BASES:
        try:
            item = model_class.objects.using(db_alias).get(id=item_id)
            item.delete(using=db_alias)
        except model_class.DoesNotExist:
            pass
    recargar_datos()

def model_crud_view(model_name, model_class, fields):
    def unique_name(name):
        def decorator(f):
            f.__name__ = f"{name}_{model_name}"
            return f
        return decorator

    @app.route(f'/{model_name}', methods=['GET'])
    @unique_name('list_view')
    def list_view():
        df = datos_concatenados.get(model_name, None)
        html = HTML_HEADER + f'<h2>{model_name.title()} - Lista</h2><a href="/{model_name}/create">Crear nuevo</a><table><tr>'
        html += ''.join(f'<th>{field.capitalize()}</th>' for field in ['ID'] + fields) + '<th>DB</th><th>Metodos</th></tr>'

        if df is not None and not df.empty:
            for db_alias in BASES:
                try:
                    qs = model_class.objects.using(db_alias).all()
                    if qs.exists():
                        item = qs.first()
                        html += f'<tr><td>{item.id}</td>'
                        for field in fields:
                            value = getattr(item, field, '')
                            html += f'<td>{value}</td>'
                        html += f'<td>{db_alias}</td>'
                        html += f'<td><a href="/{model_name}/update/{item.id}">Update</a> '
                        html += f'<a href="/{model_name}/delete/{item.id}">Delete</a></td></tr>'
                    else:
                        html += f'<tr><td>-</td>' + ''.join('<td></td>' for _ in fields) + f'<td>{db_alias}</td><td></td></tr>'
                except Exception:
                    html += f'<tr><td>Error</td>' + ''.join('<td></td>' for _ in fields) + f'<td>{db_alias}</td><td></td></tr>'
        else:
            html += f'<tr><td colspan="{len(fields) + 3}">No hay datos.</td></tr>'

        html += '</table>' + HTML_FOOTER
        return html

    @app.route(f'/{model_name}/create', methods=['GET', 'POST'])
    @unique_name('create_view')
    def create_view():
        if request.method == 'POST':
            data = {field: request.form[field] for field in fields}
            create_item(model_class, data)
            return redirect(f'/{model_name}')
        return HTML_HEADER + f'<h2>Crear {model_name.title()}</h2>' + render_form(fields, f'/{model_name}/create') + HTML_FOOTER

    @app.route(f'/{model_name}/update/<int:item_id>', methods=['GET', 'POST'])
    @unique_name('update_view')
    def update_view(item_id):
        df = datos_concatenados.get(model_name, None)
        if df is None or df[df['id'] == item_id].empty:
            return HTML_HEADER + "<p>Elemento no encontrado.</p>" + HTML_FOOTER
        if request.method == 'POST':
            data = {field: request.form[field] for field in fields}
            update_item(model_class, item_id, data)
            return redirect(f'/{model_name}')
        row = df[df['id'] == item_id].iloc[0]
        initial = {field: row.get(field, '') for field in fields}
        return HTML_HEADER + f'<h2>Editar {model_name.title()}</h2>' + render_form(fields, f'/{model_name}/update/{item_id}', initial) + HTML_FOOTER

    @app.route(f'/{model_name}/delete/<int:item_id>')
    @unique_name('delete_view')
    def delete_view(item_id):
        delete_item(model_class, item_id)
        return redirect(f'/{model_name}')

# Registrar CRUD para cada modelo con sus campos
model_crud_view('inventario', inventario, ['referencia', 'marca', 'diametro', 'categoria', 'descripcion', 'estado'])
model_crud_view('marca', marca, ['nombre_marca', 'referencia'])
model_crud_view('categoria', categoria, ['categoria', 'marca', 'referencia'])
model_crud_view('estado', estado, ['estado', 'categoria', 'marca', 'referencia'])

@app.route('/')
def home():
    return redirect('/inventario')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
