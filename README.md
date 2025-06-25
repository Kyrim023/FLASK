app_inventario = app
prueba = project

librerias:

libreria 1--pip install mysqlclient = esta se toma como la libraria que se escogio para exponer (la original es mysql-conecctor-python, pero como estamos en django, no aplica ya que es unica para python) asi que esta es la conexion de mysql a django

pip install psycopg2 = libreria para postgres


pip install psycopg = libreria para postgres


pip install psycopg2-binary = libreria postgres


libreria 2--pip install pandas = libreria de pandas


pip install django = django


libreria 3--pip install djangorestframework = complemento de django y 3 libreria encargada de la encriptacion de datos a APIs


pip install flask = esta libreria nos permite de forma mas facil y accesible, crear un front de manera basica y comprimida


archivos adicionales:


libreriap.py = en este archivo .py tenemos el uso de la libreria pandas para obtener los registros de las 3 diferentes bases de datos


flask_app.py = es el archivo que contiene la libreria de flask y la encargada de crear el front basico, utilizando las tablas que previamente nos da libreriap.py(pandas)


base de datos:


a la base de datos se le llamo "inventario", se da esta informacion ya que es necesario crear una base de datos con anterioridad tanto para mysql como para postgresql :)




>(por si alguna base de datos no quiere almacenar los datos, es un error que me paso y pense que era de codigo)
python manage.py migrate --database=mysql
python manage.py migrate --database=postgresql
python manage.py migrate --database=default


---IMPORTANTE---

Para correr el proyecto, es necesario ingresar por consola "python flask_app.py"
Esto para que el archivo corra y nos cree un puerto que sera el 5000
una vez creado el puerto, podremos darle en el link, y nos llevara automaticamente a la pagina principal, donde encontraremos las 4 tablas disponibles, y desde ahi mismo, podremos ingresar, editar o eliminar registros.
