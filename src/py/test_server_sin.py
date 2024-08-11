from flask import  Flask, jsonify
import numpy as np
from itertools import cycle

app = Flask(__name__)

angles = np.linspace(0, np.pi*2, 120)
angles_iter = cycle(angles)

@app.route("/", methods=['GET'])
def data():
    '''
    simula el funcionamiento del esp8266
    '''
    return jsonify(
        {"data":np.full((11), np.abs(100*(np.sin(next(angles_iter))))).tolist()}
    )

if __name__ =="__main__":
    app.run(debug=True, port=5000)