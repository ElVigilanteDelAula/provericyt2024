"""
Script de prueba para verificar el mapeo regional del cerebro.
Este script simula datos específicos de cada sensor para verificar 
que cada región del cerebro se active correctamente.
"""

import sys
sys.path.append('.')

from src.py.brain_viz.brain_visualizer import brain_viz
import plotly.graph_objects as go

# Simular datos de prueba con valores específicos para cada sensor
test_data = {
    'uid': '20250924120000',
    'sensor_a': {  # Centro - debe activar centro del cerebro
        'attention': 80,    # Alto = rojo
        'meditation': 20,   # Bajo = azul
        'signal_strength': 75
    },
    'sensor_b': {  # Lateral superior izquierdo
        'attention': 20,    # Bajo = azul
        'meditation': 80,   # Alto = rojo  
        'signal_strength': 75
    },
    'sensor_c': {  # Lateral superior derecho
        'attention': 90,    # Muy alto = muy rojo
        'meditation': 10,   # Muy bajo = muy azul
        'signal_strength': 75
    },
    'sensor_d': {  # Lateral inferior izquierdo
        'attention': 10,    # Muy bajo = muy azul
        'meditation': 90,   # Muy alto = muy rojo
        'signal_strength': 75
    },
    'sensor_e': {  # Lateral inferior derecho
        'attention': 70,    # Alto = rojo
        'meditation': 30,   # Bajo = azul
        'signal_strength': 75
    }
}

print("Creando figura de prueba con datos específicos por sensor...")
print(f"Sensor A (centro): attention={test_data['sensor_a']['attention']}, meditation={test_data['sensor_a']['meditation']}")
print(f"Sensor B (sup. izq): attention={test_data['sensor_b']['attention']}, meditation={test_data['sensor_b']['meditation']}")
print(f"Sensor C (sup. der): attention={test_data['sensor_c']['attention']}, meditation={test_data['sensor_c']['meditation']}")
print(f"Sensor D (inf. izq): attention={test_data['sensor_d']['attention']}, meditation={test_data['sensor_d']['meditation']}")
print(f"Sensor E (inf. der): attention={test_data['sensor_e']['attention']}, meditation={test_data['sensor_e']['meditation']}")

# Crear figura con datos de prueba - MODO TODOS
print("\n=== PROBANDO MODO 'TODOS' ===")
fig_all = brain_viz.create_live_brain_figure(test_data)

if fig_all:
    print("✅ Figura TODOS creada exitosamente!")
    print("🧠 Deberías ver activación en todas las regiones:")
    print("   - Centro: Rojo (sensor A - alta atención)")  
    print("   - Superior izquierdo: Rojo (sensor B - alta meditación)")
    print("   - Superior derecho: Muy rojo (sensor C - muy alta atención)")
    print("   - Inferior izquierdo: Muy rojo (sensor D - muy alta meditación)")
    print("   - Inferior derecho: Rojo (sensor E - alta atención)")
    
    # Mostrar la figura
    fig_all.show()
else:
    print("❌ Error al crear la figura TODOS")

# Probar modo INDIVIDUAL - solo sensor A
print("\n=== PROBANDO MODO 'INDIVIDUAL' - SENSOR A ===")
sensor_a_data = {
    'uid': test_data['uid'],
    'sensor_a': test_data['sensor_a']
}

fig_a = brain_viz.create_live_brain_figure(sensor_a_data)
if fig_a:
    print("✅ Figura SENSOR A creada exitosamente!")
    print("🧠 Solo deberías ver activación en el centro del cerebro")
    fig_a.show()
else:
    print("❌ Error al crear la figura SENSOR A")

# Probar modo INDIVIDUAL - solo sensor C
print("\n=== PROBANDO MODO 'INDIVIDUAL' - SENSOR C ===")
sensor_c_data = {
    'uid': test_data['uid'],
    'sensor_c': test_data['sensor_c']
}

fig_c = brain_viz.create_live_brain_figure(sensor_c_data)
if fig_c:
    print("✅ Figura SENSOR C creada exitosamente!")
    print("🧠 Solo deberías ver activación en el lateral superior derecho")
    fig_c.show()
else:
    print("❌ Error al crear la figura SENSOR C")