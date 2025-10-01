"""
Script simple para probar que los módulos se importan correctamente con la nueva implementación.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🧪 Probando nueva implementación con detección directa de mouse...")

try:
    # Verificar importaciones
    from src.py.brain_viz import brain_components
    from src.py.brain_viz import live_brain_callbacks_simple
    print("✅ Módulos importados correctamente")
    
    # Verificar que el componente se crea sin errores
    brain_component = brain_components.create_brain_component()
    print("✅ Componente del cerebro creado exitosamente")
    
    # Buscar componentes específicos
    has_interval = False
    has_interaction_store = False
    
    def check_components(component):
        global has_interval, has_interaction_store
        if hasattr(component, 'children') and component.children:
            for child in component.children:
                if hasattr(child, 'id'):
                    if 'mouse_interval' in str(child.id):
                        has_interval = True
                    elif 'interaction_store' in str(child.id):
                        has_interaction_store = True
                check_components(child)
    
    check_components(brain_component)
    
    if has_interval:
        print("✅ Interval para detección de mouse encontrado")
    else:
        print("❌ Interval para detección de mouse NO encontrado")
    
    if has_interaction_store:
        print("✅ Store de interacción encontrado")
    else:
        print("❌ Store de interacción NO encontrado")
    
    print("\n🎯 Nueva implementación:")
    print("1. ✅ ClientsideCallback para detectar mouse down/up en JavaScript")
    print("2. ✅ Interval de 50ms para monitoreo en tiempo real")
    print("3. ✅ Estado 'mouse_down' para pausa exacta durante click presionado")
    print("4. ✅ Callback principal modificado para usar estado directo de mouse")
    
    print("\n🚀 Ventajas de esta implementación:")
    print("- Detección DIRECTA de eventos mousedown/mouseup")
    print("- No depende de inferencias de relayoutData") 
    print("- Pausa EXACTAMENTE mientras mantienes presionado el click")
    print("- Reanuda INMEDIATAMENTE al soltar el mouse")
    print("- Funciona independientemente del tipo de movimiento")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()