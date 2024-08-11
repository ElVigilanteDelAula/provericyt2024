# UwU

## Aplicaciones

+ `app.py` es un explorador de la base de datos
+ `live_app.py` es un visualizador de los datos en vivo
    + Se tiene que duplicar el archivo `config_template.json` y renombrarlo a config, con los valores apropiados para cada caso

Adicionalmente hay dos servidores de datos de prueba, que emulan la salida que esperamos del ESP

+ `test_server.py` es un servidor de prueba que da datos aleatorios entre 0 y 100
+ `test_server_sine.py` es un servidor de prueba que da una señal de seno entre 0 y 100

## Librerías

Utilizando Python 3.12.4

+ Flask
+ Plotly
+ Dash
+ Dash bootstrap components
+ Requests

+ Hay que renombrar config_template a config, con los valores que se usaràn

# Flujo

+ Se obtienen los datos del mindflex con el esp8266
+ Se obtienen los datos del esp8266 con la librería Requests
+ Se guardan todos los datos obtenidos a una base de datos de SQLite
+ Se grafican parte de los datos obtenidos en el momento con Dash/plotly

## Estructura

+ En `src/py/database/database.py` se encuentra el codigo que se usa para guardar los datos en la base de datos.

+ En `src/py/utils/utils.py` se encuentran varias funciones que aun no tienen un lugar predeterminado.

+ En `src/py/gui` y `src/py/live_gui` se encuentran los archivos de dash para construir la aplicación correspondiente