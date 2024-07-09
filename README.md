# UwU

##
Librerias que se usan

+ Flask
+ Plotly
+ Dash
+ Dash bootstrap components
+ Dash bootstrap templates
+ Requests

+ Hay que renombrar config_template a config, con los valores que se usaràn

# Flujo

+ Se obtienen los datos del mindflex con el esp8266
+ Se obtienen los datos del esp8266 con la librería ´Requests´
+ Se guardan todos los datos obtenidos a una base de datos de SQLite
+ Se grafican parte de los datos obtenidos en el momento con Dash/plotly

# Cosas que podria cambiar
+ el diseño de las bases de datos es sus
+ logs apropiados para errores
+ declarar tipo de datos en la funcion que crea las tablas para las sesiones
+ faltas de ortografía
+ crear wrappers para las instrucciones de la base de datos, pero es que es mas legible con el sql ahi
+ revisar callbacks del lado del cliente para que sea mas eficiente la grafica
+ Tiene que haber una mejor manera de implementar los parametros del sensor para la base de datos
+ puede que esa no sea la manera de usar un archivo de configuracion
+ tiene que haber una mejor manera de checar si las tablas estan creadas

## Estructura

En `src\py\database` se encuentra el codigo que se usa para guardar los datos en la base de datos.

En `src\py\utils` se encuentran varias funciones que aun no tienen un lugar predeterminado.

El archivo `test_server.py` en `src\py` tiene un servidor que se puede correr para simular los datos que devuelve la placa ESP.

La aplicación principal se encuentra en el archivo `app.py`