"""
Script de prueba para verificar el efecto heatmap del cerebro.
Prueba diferentes valores de signal_strength para mostrar:
1. Control de área de cobertura
2. Efecto de desvanecimiento radial
"""

import sys
sys.path.append('.')

from src.py.brain_viz.brain_visualizer import brain_viz
import plotly.graph_objects as go

print("🧠 PROBANDO EFECTO HEATMAP CON SIGNAL_STRENGTH")
print("=" * 50)

# Test 1: Signal strength baja (área pequeña)
print("\n📡 TEST 1: SIGNAL STRENGTH BAJA (20%) - Área pequeña")
test_data_low = {
    'uid': '20250925120000',
    'sensor_a': {  # Centro
        'attention': 90,        # Muy alta atención = rojo intenso
        'meditation': 20,       # Baja meditación  
        'signal_strength': 20   # 🔸 Señal débil = área pequeña
    },
    'sensor_c': {  # Superior derecho
        'attention': 80,        # Alta atención
        'meditation': 30,       
        'signal_strength': 20   # 🔸 Señal débil = área pequeña
    }
}

fig_low = brain_viz.create_live_brain_figure(test_data_low)
if fig_low:
    print("✅ Creado - Deberías ver áreas PEQUEÑAS con desvanecimiento gradual")
    fig_low.show()

# Test 2: Signal strength media (área media)
print("\n📡 TEST 2: SIGNAL STRENGTH MEDIA (60%) - Área media")
test_data_medium = {
    'uid': '20250925120000',
    'sensor_a': {  # Centro
        'attention': 90,        # Muy alta atención = rojo intenso
        'meditation': 20,       # Baja meditación  
        'signal_strength': 60   # 🔶 Señal media = área media
    },
    'sensor_c': {  # Superior derecho
        'attention': 80,        # Alta atención
        'meditation': 30,       
        'signal_strength': 60   # 🔶 Señal media = área media
    }
}

fig_medium = brain_viz.create_live_brain_figure(test_data_medium)
if fig_medium:
    print("✅ Creado - Deberías ver áreas MEDIANAS con desvanecimiento gradual")
    fig_medium.show()

# Test 3: Signal strength alta (área grande)
print("\n📡 TEST 3: SIGNAL STRENGTH ALTA (100%) - Área grande")
test_data_high = {
    'uid': '20250925120000',
    'sensor_a': {  # Centro
        'attention': 90,        # Muy alta atención = rojo intenso
        'meditation': 20,       # Baja meditación  
        'signal_strength': 100  # 🔴 Señal fuerte = área grande
    },
    'sensor_c': {  # Superior derecho
        'attention': 80,        # Alta atención
        'meditation': 30,       
        'signal_strength': 100  # 🔴 Señal fuerte = área grande
    }
}

fig_high = brain_viz.create_live_brain_figure(test_data_high)
if fig_high:
    print("✅ Creado - Deberías ver áreas GRANDES con desvanecimiento gradual")
    fig_high.show()

# Test 4: Comparación de múltiples sensores con diferentes signal strengths
print("\n📡 TEST 4: MÚLTIPLES SENSORES CON DIFERENTES SIGNAL STRENGTHS")
test_data_mixed = {
    'uid': '20250925120000',
    'sensor_a': {  # Centro - señal fuerte
        'attention': 90,
        'meditation': 20,
        'signal_strength': 100  # Área GRANDE
    },
    'sensor_b': {  # Sup. izq - señal débil  
        'attention': 80,
        'meditation': 30,
        'signal_strength': 30   # Área PEQUEÑA
    },
    'sensor_c': {  # Sup. der - señal media
        'attention': 85,
        'meditation': 25,
        'signal_strength': 65   # Área MEDIANA
    },
    'sensor_d': {  # Inf. izq - señal muy débil
        'attention': 70,
        'meditation': 40,
        'signal_strength': 15   # Área MUY PEQUEÑA
    },
    'sensor_e': {  # Inf. der - señal fuerte
        'attention': 95,
        'meditation': 15,
        'signal_strength': 95   # Área GRANDE
    }
}

fig_mixed = brain_viz.create_live_brain_figure(test_data_mixed)
if fig_mixed:
    print("✅ Creado - Deberías ver:")
    print("   🔴 Centro: Área GRANDE (signal=100)")
    print("   🔸 Sup. izq: Área PEQUEÑA (signal=30)")  
    print("   🔶 Sup. der: Área MEDIANA (signal=65)")
    print("   🔹 Inf. izq: Área MUY PEQUEÑA (signal=15)")
    print("   🔴 Inf. der: Área GRANDE (signal=95)")
    print("   💡 Todas con desvanecimiento gradual desde el centro!")
    fig_mixed.show()

print("\n🎯 CARACTERÍSTICAS DEL HEATMAP:")
print("• Signal strength 0-100 controla área de cobertura (10%-100%)")
print("• Intensidad máxima en el centro de cada región")  
print("• Desvanecimiento gradual hacia los bordes")
print("• Color basado en attention/meditation values")
print("• Múltiples regiones pueden superponerse")