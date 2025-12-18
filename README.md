# UwU

## Instalación rápida (obligatoria)

1. Crea tu entorno virtual y ejecuta `pip install -r requirements.txt`.
2. **Siempre** corre `python check_setup.py` antes del primer uso (y cada vez que cambies de máquina) para validar que todas las dependencias, datos de `nilearn` y configuraciones locales estén correctas.
3. Si el script marca algún error, sigue las instrucciones que imprime y vuelve a ejecutarlo hasta ver todos los checks en verde.

## Configuración de `config.json`


1. Duplica `config_template.json` y renómbralo como `config.json` en la raíz del proyecto.
2. Ajusta los valores según tu entorno:
     - `database_path`: archivo SQLite donde se guardarán las sesiones (p.ej. `test.db`).
     - `parameters`: lista de métricas que reportan los sensores (debe coincidir con el orden real del dispositivo).
     - `parameter_map`: mapa nombre → índice para interpretar cada lectura.
     - `sensors`: URLs de cada sensor/ESP8266 que entrega los datos.
     - `sensors_map`: asigna a cada sensor el índice que se usará en la BD y las gráficas.
     - `events`: catálogo de eventos/etiquetas que se podrán registrar desde la UI.

Ejemplo de estructura (usa tus propias direcciones IP y parámetros reales):

```json
{
    "database_path": "test.db",
    "parameters": ["signal_strength", "attention", "meditation", "delta", "theta", "low_alpha", "high_alpha", "low_beta", "high_beta", "low_gamma", "high_gamma"],
    "parameter_map": {"signal_strength": 0, "attention": 1, "meditation": 2, "delta": 3, "theta": 4, "low_alpha": 5, "high_alpha": 6, "low_beta": 7, "high_beta": 8, "low_gamma": 9, "high_gamma": 10},
    "sensors": {
        "sensor_a": "http://127.0.0.1:5000/",
        "sensor_b": "http://127.0.0.1:5000/",
        "sensor_c": "http://127.0.0.1:5000/",
        "sensor_d": "http://127.0.0.1:5000/",
        "sensor_e": "http://127.0.0.1:5000/"
    },
    "sensors_map": {"sensor_a": 0, "sensor_b": 1, "sensor_c": 2, "sensor_d": 3, "sensor_e": 4},
    "events": {"evento1": "tag1", "evento2": "tag2"}
}
```

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