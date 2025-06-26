import pandas as pd
import os
import sys
import django

# Solo configurar Django si no está configurado ya
if not django.conf.settings.configured:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'prueba.settings')
    django.setup()

from app_inventario.models import inventario, marca, categoria, estado

BASES = ['default', 'mysql', 'postgresql']

MODELOS = {
    'inventario': inventario,
    'marca': marca,
    'categoria': categoria,
    'estado': estado
}

def cargar_desde_modelo(model, db_alias):
    qs = model.objects.using(db_alias).all()
    data = list(qs.values())
    df = pd.DataFrame(data)
    return df

def cargar_todos():
    datos = {nombre: {} for nombre in MODELOS.keys()}
    for nombre, modelo in MODELOS.items():
        for base in BASES:
            df = cargar_desde_modelo(modelo, base)
            datos[nombre][base] = df
    return datos

def concatenar_todos(datos):
    datos_concatenados = {}
    for nombre in datos.keys():
        dfs = [datos[nombre][base] for base in BASES if not datos[nombre][base].empty]
        if dfs:
            df_concat = pd.concat(dfs, ignore_index=True)
        else:
            df_concat = pd.DataFrame()
        datos_concatenados[nombre] = df_concat
    return datos_concatenados