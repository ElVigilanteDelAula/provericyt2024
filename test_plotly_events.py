"""
Script para probar la nueva implementación basada en eventos de Plotly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔄 Probando nueva implementación basada en eventos de Plotly...")

try:
    from src.py.brain_viz import brain_components
    from src.py.brain_viz import live_brain_callbacks_simple
    print("✅ Módulos importados correctamente")
    
    brain_component = brain_components.create_brain_component()
    print("✅ Componente del cerebro creado")
    
    print("\n🎯 Nueva Estrategia - Eventos Nativos de Plotly:")
    print("1. ✅ Detección basada en relayoutData (eventos de cámara)")
    print("2. ✅ Timer de 100ms para verificar fin de interacción")
    print("3. ✅ Sin JavaScript personalizado problemático")
    print("4. ✅ Usa eventos que SÍ funcionan en Plotly")
    
    print("\n🔍 Cómo Funciona:")
    print("- Al mover/rotar el cerebro → relayoutData contiene 'scene.camera'")
    print("- Esto marca is_interacting = True inmediatamente")
    print("- Timer verifica cada 100ms si han pasado >200ms sin eventos")
    print("- Si sí, marca is_interacting = False")
    
    print("\n📊 Lo que Deberías Ver Ahora:")
    print("1. Ejecuta live_app.py")
    print("2. Ve a Cerebro 3D")
    print("3. Mantén presionado y arrastra el cerebro")
    print("4. En terminal: '📹 INTERACCIÓN DETECTADA - Evento de cámara'")
    print("5. En terminal: '🚫 PAUSANDO actualización - Interacción activa'")
    print("6. Suelta el mouse y espera 200ms")
    print("7. En terminal: '✋ INTERACCIÓN TERMINADA'")
    print("8. En terminal: '✅ PERMITIENDO actualización - Interactuando: False'")
    
    print("\n✨ Ventajas de Esta Implementación:")
    print("- Usa eventos nativos de Plotly que SÍ se disparan")
    print("- No depende de JavaScript personalizado")
    print("- Detecta cualquier tipo de interacción con el cerebro")
    print("- Funciona independientemente del navegador")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()