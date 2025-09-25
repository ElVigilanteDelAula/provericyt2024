"""
Servidor de prueba mejorado para demostrar el efecto heatmap.
Genera datos EEG variados con diferentes valores de signal_strength.
"""
from flask import Flask, jsonify
import numpy as np
import time
import math

app = Flask(__name__)
rng = np.random.default_rng()

# Contador global para crear patrones dinámicos
request_count = 0

@app.route("/", methods=['GET'])
def data():
    '''
    Simula el funcionamiento del esp8266 con datos variados para heatmap.
    Cada llamada genera un patrón diferente de signal_strength y valores EEG.
    '''
    global request_count
    request_count += 1
    
    # Crear patrones que cambian con el tiempo para mostrar el efecto heatmap
    time_factor = request_count * 0.1
    
    # Generar datos de prueba con patrones específicos
    eeg_data = []
    
    # Índices según el mapeo en config.json:
    # 0: signal_strength, 1: attention, 2: meditation, 3-10: ondas cerebrales
    
    for i in range(11):
        if i == 0:  # signal_strength - varía de 20 a 100 con patrón sinusoidal
            base_strength = 60 + 35 * math.sin(time_factor + request_count * 0.05)
            strength = max(20, min(100, base_strength + rng.normal(0, 10)))
            eeg_data.append(int(strength))
            
        elif i == 1:  # attention - patrón dinámico
            base_attention = 50 + 30 * math.cos(time_factor * 0.8)
            attention = max(10, min(100, base_attention + rng.normal(0, 8)))
            eeg_data.append(int(attention))
            
        elif i == 2:  # meditation - patrón inverso a attention
            base_meditation = 50 + 25 * math.sin(time_factor * 0.6 + math.pi)
            meditation = max(10, min(100, base_meditation + rng.normal(0, 8)))
            eeg_data.append(int(meditation))
            
        else:  # ondas cerebrales (delta, theta, alphas, betas, gammas)
            base_wave = 40 + 20 * math.sin(time_factor * 0.3 + i)
            wave = max(5, min(95, base_wave + rng.normal(0, 12)))
            eeg_data.append(int(wave))
    
    # Añadir algo de variación aleatoria para simular datos más realistas
    for i in range(len(eeg_data)):
        eeg_data[i] = max(0, min(100, eeg_data[i] + rng.integers(-5, 6)))
    
    # Log para debug (opcional)
    if request_count % 10 == 0:  # Log cada 10 requests
        print(f"Request {request_count}: signal_strength={eeg_data[0]}, attention={eeg_data[1]}, meditation={eeg_data[2]}")
    
    return jsonify({"data": eeg_data})

if __name__ == "__main__":
    print("🧠 Servidor EEG Heatmap iniciado!")
    print("📡 Generando datos variados para demostrar efecto heatmap:")
    print("   • Signal strength: 20-100 (controla área de cobertura)")
    print("   • Attention/Meditation: patrones dinámicos")
    print("   • Ondas cerebrales: simulación realista")
    print("🌐 Servidor corriendo en http://127.0.0.1:5000")
    app.run(debug=True, port=5000)