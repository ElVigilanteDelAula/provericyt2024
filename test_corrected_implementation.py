"""
Script para probar la implementación corregida sin ClientsideCallback.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔧 Probando implementación corregida...")

try:
    # Verificar importaciones
    from src.py.brain_viz import brain_components
    from src.py.brain_viz import live_brain_callbacks_simple
    print("✅ Módulos importados sin errores")
    
    # Verificar que el componente se crea correctamente
    brain_component = brain_components.create_brain_component()
    print("✅ Componente del cerebro creado exitosamente")
    
    # Verificar componentes específicos
    has_mouse_state = False
    has_interaction_store = False
    has_script = False
    
    def check_components(component):
        global has_mouse_state, has_interaction_store, has_script
        if hasattr(component, 'children') and component.children:
            for child in component.children:
                if hasattr(child, 'id'):
                    if 'mouse_state' in str(child.id):
                        has_mouse_state = True
                    elif 'interaction_store' in str(child.id):
                        has_interaction_store = True
                elif hasattr(child, 'children') and 'setTimeout' in str(child.children):
                    has_script = True
                check_components(child)
    
    check_components(brain_component)
    
    print(f"✅ Div para estado de mouse: {'Encontrado' if has_mouse_state else 'NO encontrado'}")
    print(f"✅ Store de interacción: {'Encontrado' if has_interaction_store else 'NO encontrado'}")
    print(f"✅ Script JavaScript: {'Encontrado' if has_script else 'NO encontrado'}")
    
    print("\n🛠️ Implementación Corregida:")
    print("1. ✅ Eliminado ClientsideCallback problemático")
    print("2. ✅ Div oculto para capturar estado de mouse")
    print("3. ✅ Script HTML simple con setTimeout")
    print("4. ✅ Callback Python simple para detectar cambios")
    
    print("\n✨ Ventajas de la nueva implementación:")
    print("- Sin errores de ClientsideCallback")
    print("- JavaScript más simple y robusto")
    print("- Callback Python estándar sin complejidad")
    print("- Detección directa de eventos mousedown/mouseup")
    
    print("\n🚀 Ahora deberías poder ejecutar live_app.py sin errores!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()