"""
Script para probar la implementación mejorada con debug completo.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 Probando implementación mejorada con debug...")

try:
    from src.py.brain_viz import brain_components
    from src.py.brain_viz import live_brain_callbacks_simple
    print("✅ Módulos importados correctamente")
    
    brain_component = brain_components.create_brain_component()
    print("✅ Componente del cerebro creado")
    
    print("\n🛠️ Implementación Mejorada con Debug:")
    print("1. ✅ Div oculto para estado de mouse")
    print("2. ✅ Div visible para debug en tiempo real")
    print("3. ✅ JavaScript mejorado con console.log")
    print("4. ✅ Callback con debug prints en Python")
    print("5. ✅ Múltiples intentos de configuración de event listeners")
    
    print("\n🔍 Cómo Debuggear:")
    print("1. Ejecuta live_app.py")
    print("2. Ve a la pestaña Cerebro 3D")
    print("3. Abre la consola del navegador (F12)")
    print("4. Mantén presionado el click en el cerebro")
    print("5. Verifica en consola: 'Mouse down detectado en cerebro'")
    print("6. Verifica en terminal Python: '🚫 PAUSANDO actualización'")
    print("7. Suelta el mouse")
    print("8. Verifica en consola: 'Mouse up detectado globalmente'")
    print("9. Verifica en terminal Python: '✅ PERMITIENDO actualización'")
    
    print("\n📍 Indicadores Visuales:")
    print("- Esquina superior derecha del cerebro: 'Mouse: UP' / 'Mouse: DOWN (PAUSADO)'")
    print("- Terminal Python: Mensajes de debug detallados")
    print("- Consola del navegador: Logs de JavaScript")
    
    print("\n🎯 Si aún no funciona, verifica:")
    print("- ¿Se muestran los logs de JavaScript en la consola?")
    print("- ¿Cambia el indicador visual al presionar/soltar?")
    print("- ¿Se muestran los mensajes de Python en terminal?")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()