from flask import  Flask, jsonify
import numpy as np

app = Flask(__name__)

@app.route("/", methods=['GET'])
def data():
    '''
    simula el funcionamiento del esp8266
    '''
    return jsonify(
        {"data":np.random.random_sample((11)).tolist()}
    )