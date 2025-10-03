"""
Callbacks simplificados para actualizaciones de visualización del cerebro en vivo.
Usa uirevision de Plotly para preservar automáticamente la posición de la cámara.
INCLUYE TIMELINE interactivo para navegación temporal de la sesión actual.

ESTRATEGIA PROACTIVA de detección de interacción:
1. Mouse tracker global: mousedown/mouseup en el área de la gráfica
2. relayoutData: Cualquier evento pausa por 2s (backup confiable)
3. Timer: Auto-reset después de 2s sin actividad
4. TIMELINE: Click en timeline pausa actualizaciones automáticas
"""

import plotly.graph_objects as go
import time
from dash import Input, Output, State, no_update, ctx, html
from src.py.brain_viz.brain_visualizer import brain_viz
from src.py.brain_viz.simple_timeline_callbacks import register_simple_timeline_callbacks


def register_brain_callbacks(app):
    """Registrar callbacks del cerebro con la aplicación Dash."""
    
    # Registrar callbacks del timeline simplificado
    register_simple_timeline_callbacks(app)
    
    # ClientsideCallback simplificado para detección de mouse
    app.clientside_callback(
        """
        function(n_intervals) {
            try {
                // Estado simple para tracking de mouse
                if (typeof window.mouseTracker === 'undefined') {
                    window.mouseTracker = {
                        isPressed: false,
                        lastUpdate: 0
                    };
                    
                    // Instalar listeners globales una sola vez
                    document.addEventListener('mousedown', function(e) {
                        // Solo si es en el área de la gráfica
                        const target = e.target;
                        const graphContainer = document.getElementById('brain_graph');
                        if (graphContainer && graphContainer.contains(target)) {
                            console.log('🖱️ MOUSEDOWN en gráfica - PAUSANDO');
                            window.mouseTracker.isPressed = true;
                            window.mouseTracker.lastUpdate = Date.now() / 1000;
                        }
                    });
                    
                    document.addEventListener('mouseup', function(e) {
                        if (window.mouseTracker.isPressed) {
                            console.log('🖱️ MOUSEUP detectado - REANUDANDO');
                            window.mouseTracker.isPressed = false;
                            window.mouseTracker.lastUpdate = Date.now() / 1000;
                        }
                    });
                    
                    console.log('✅ Mouse tracker instalado globalmente');
                }
                
                return {
                    is_interacting: window.mouseTracker.isPressed,
                    last_interaction: window.mouseTracker.lastUpdate
                };
                
            } catch (error) {
                console.error('Error en mouse tracker:', error);
                return {is_interacting: false, last_interaction: 0};
            }
        }
        """,
        Output('brain_interaction_store', 'data', allow_duplicate=True),
        [Input('interaction_timer', 'n_intervals')],
        prevent_initial_call=True
    )

    # ALTERNATIVA: Si el ClientsideCallback falla, usar solo Python con detección más agresiva
    @app.callback(
        Output('brain_interaction_store', 'data', allow_duplicate=True),
        [Input('brain_graph', 'relayoutData'),
         Input('interaction_timer', 'n_intervals')],
        [State('brain_interaction_store', 'data')],
        prevent_initial_call=True
    )
    def handle_brain_interaction_backup(relayout_data, n_intervals, interaction_state):
        """
        Callback de backup para detección de interacción cuando falla el clientside.
        Solo actualiza cuando detecta actividad en relayoutData.
        """
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        if not interaction_state:
            interaction_state = {'is_interacting': False, 'last_interaction': 0}
        
        if triggered_id == 'brain_graph' and relayout_data:
            # Relayout detectado - pausar por 2 segundos
            current_time = time.time()
            print(f"🎯 RELAYOUT DETECTADO - PAUSANDO por 2s")
            return {
                'is_interacting': True,
                'last_interaction': current_time
            }
        
        elif triggered_id == 'interaction_timer':
            # Timer tick - revisar si hay que reanudar
            current_time = time.time()
            last_interaction = interaction_state.get('last_interaction', 0)
            
            # Auto-reanudar después de 2 segundos sin actividad
            if current_time - last_interaction > 2.0 and interaction_state.get('is_interacting'):
                print(f"⏰ AUTO-REANUDANDO después de 2s")
                return {
                    'is_interacting': False,
                    'last_interaction': last_interaction
                }
            
            return interaction_state
        
        # Mantener estado actual
        return interaction_state

    @app.callback(
        [Output('brain_graph', 'figure'),
         Output('brain_camera_store', 'data')],
        [Input('timer', 'n_intervals'),
         Input('memory', 'data'),
         Input('sensor_select', 'value'),
         Input('quantity_select', 'value'),
         Input('simple_timeline_mode', 'data')],  # Usar el nuevo timeline simplificado
        [State('brain_camera_store', 'data'),
         State('brain_interaction_store', 'data')]
    )
    def update_brain_visualization(n_intervals, data, selected_sensor, quantity_mode, 
                                  timeline_mode, camera_state, interaction_state):
        """
        Callback principal para actualizar la visualización del cerebro 3D.
        Usa el nuevo timeline simplificado.
        """
        import time
        
        # Debug simplificado
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # VERIFICACION DE TIMELINE SIMPLIFICADO
        display_data = data  # Por defecto usar datos actuales
        mode = timeline_mode.get('mode', 'live') if timeline_mode else 'live'
        
        # Si estamos en modo histórico, usar datos guardados
        if mode == 'historical' and timeline_mode.get('selected_data'):
            display_data = timeline_mode['selected_data']
            print(f"🕒 MODO HISTÓRICO: Usando datos de t={timeline_mode.get('selected_time', 0):.1f}s")
        
        # VERIFICACION DE INTERACCION
        should_pause = False
        if interaction_state:
            should_pause = interaction_state.get('is_interacting', False)
        
        # Pausar solo si hay interacción activa Y estamos en modo live
        if should_pause and triggered_id in ['timer', 'memory'] and mode == 'live':
            print(f"🚫 PAUSADO - interacción activa en modo live")
            return no_update, no_update
        
        # Pausar si estamos en modo pausado
        if mode == 'paused' and triggered_id in ['timer', 'memory']:
            print(f"⏸️ PAUSADO - modo pausado del timeline")
            return no_update, no_update
        
        if not display_data or 'uid' not in display_data:
            print(f"❌ No hay datos válidos")
            return go.Figure().add_annotation(
                text="Esperando datos de la sesión...",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            ), camera_state
        
        # Continuar con actualización normal
        try:
            session_uid = display_data['uid']
            
            print(f"🔄 PROCESANDO DATOS - uid: {session_uid}, modo: {quantity_mode}, timeline: {mode}")
            
            # Obtener datos de sensores según el modo seleccionado
            if quantity_mode == 'todos':
                # Mostrar todos los sensores disponibles
                sensors_data = {k: v for k, v in display_data.items() if k != 'uid' and v is not None}
                sensors_data['uid'] = session_uid
            else:  # modo 'individual'
                # Usar solo el sensor seleccionado
                if selected_sensor in display_data:
                    sensors_data = {selected_sensor: display_data[selected_sensor], 'uid': session_uid}
                else:
                    print(f"❌ Sensor {selected_sensor} no encontrado")
                    return go.Figure().add_annotation(
                        text=f"No hay datos para: {selected_sensor}",
                        xref="paper", yref="paper", x=0.5, y=0.5,
                        showarrow=False, font=dict(size=16)
                    ), camera_state
            
            if len(sensors_data) <= 1:  # Solo contiene 'uid'
                print(f"❌ Datos insuficientes")
                return go.Figure().add_annotation(
                    text="No hay datos de sensores disponibles",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=16)
                ), camera_state
            
            # Crear nueva figura del cerebro
            print(f"🔄 Creando figura con {len(sensors_data)-1} sensores")
            new_figure = brain_viz.create_live_brain_figure(sensors_data)
            
            # Agregar indicador del modo timeline al título
            if mode == 'historical':
                selected_time = timeline_mode.get('selected_time', 0)
                current_title = new_figure.layout.title.text if new_figure.layout.title else "Visualización Cerebro 3D"
                new_figure.update_layout(
                    title=f"{current_title}<br><span style='color: orange; font-size: 12px;'>🕒 Modo Histórico: t={selected_time:.1f}s</span>"
                )
            elif mode == 'paused':
                current_title = new_figure.layout.title.text if new_figure.layout.title else "Visualización Cerebro 3D"
                new_figure.update_layout(
                    title=f"{current_title}<br><span style='color: gray; font-size: 12px;'>⏸️ Pausado</span>"
                )
            
            # Aplicar cámara guardada si existe
            if camera_state and new_figure and 'layout' in new_figure:
                if 'scene' not in new_figure['layout']:
                    new_figure['layout']['scene'] = {}
                
                # Verificar que camera_state tenga la estructura correcta
                # Puede ser: {'eye': {...}, 'center': {...}, 'up': {...}}
                # O puede ser: {'camera': {'eye': {...}, ...}}
                if camera_state:
                    # Detectar si tiene estructura anidada incorrecta
                    if 'camera' in camera_state:
                        camera_config = camera_state['camera']
                    elif any(k in camera_state for k in ['eye', 'center', 'up', 'projection']):
                        camera_config = camera_state
                    else:
                        camera_config = None
                    
                    if camera_config:
                        # Limpiar cualquier clave 'scene' incorrecta
                        clean_camera = {k: v for k, v in camera_config.items() 
                                       if k in ['eye', 'center', 'up', 'projection']}
                        
                        if clean_camera:
                            new_figure['layout']['scene']['camera'] = clean_camera
                            print(f"✅ Aplicada cámara guardada: {list(clean_camera.keys())}")
            
            print(f"✅ CEREBRO ACTUALIZADO: modo={mode}, sensores={len(sensors_data)-1}, uid={session_uid}")
            return new_figure, camera_state
            
        except Exception as e:
            print(f"❌ Error en callback: {e}")
            return go.Figure().add_annotation(
                text=f"Error: {str(e)}",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16, color="red")
            ), camera_state


    @app.callback(
        Output('brain_camera_store', 'data', allow_duplicate=True),
        [Input('brain_graph', 'relayoutData')],
        [State('brain_camera_store', 'data')],
        prevent_initial_call=True
    )
    def store_brain_camera_state(relayout_data, current_state):
        """
        Callback para capturar y guardar cambios de cámara del usuario.
        Funciona como respaldo al uirevision para máxima robustez.
        """
        if not relayout_data:
            return current_state
        
        # Buscar datos de cámara en relayoutData
        camera_data = {}
        has_camera_data = False
        
        for key, value in relayout_data.items():
            if 'scene.camera' in key:
                has_camera_data = True
                # Extraer solo la parte después de 'scene.camera.'
                # Ej: 'scene.camera.eye.x' -> ['eye', 'x']
                camera_path = key.replace('scene.camera.', '')
                keys = camera_path.split('.')
                
                # Construir estructura jerárquica correctamente
                current = camera_data
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
        
        if has_camera_data:
            # Validar que no haya claves incorrectas
            valid_keys = {'eye', 'center', 'up', 'projection'}
            camera_data = {k: v for k, v in camera_data.items() if k in valid_keys}
            
            if camera_data:
                print(f"📷 Guardando nueva posición de cámara: {list(camera_data.keys())}")
                return camera_data
        
        # Si no hay datos de cámara pero sí relayoutData, mantener estado actual
        return current_state if current_state else {}
