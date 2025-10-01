"""
Callbacks simplificados para actualizaciones de visualización del cerebro en vivo.
Usa uirevision de Plotly para preservar automáticamente la posición de la cámara.
ESTRATEGIA PROACTIVA de detección de interacción:
1. Mouse tracker global: mousedown/mouseup en el área de la gráfica
2. relayoutData: Cualquier evento pausa por 2s (backup confiable)
3. Timer: Auto-reset después de 2s sin actividad
"""

import plotly.graph_objects as go
import time
from dash import Input, Output, State, no_update, ctx, ClientsideFunction
from src.py.brain_viz.brain_visualizer import brain_viz


def register_brain_callbacks(app):
    """Registrar callbacks del cerebro con la aplicación Dash."""
    
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
    def detect_interaction_hybrid(relayout_data, n_intervals, interaction_state):
        """
        ESTRATEGIA PROACTIVA: 
        1. ClientsideCallback: Detección global de mousedown/mouseup 
        2. relayoutData: Cualquier evento = pausa proactiva por 2s
        3. Timer: Auto-reset después de 2s sin eventos
        """
        import time
        from dash import callback_context
        
        ctx = callback_context
        triggered_id = ctx.triggered_id if ctx.triggered else None
        current_time = time.time()
        
        # Inicializar estado si no existe
        if not interaction_state:
            interaction_state = {'is_interacting': False, 'last_interaction': 0}
        
        print(f"� HIBRIDO: triggered={triggered_id}, relayout={bool(relayout_data)}")
        
        # Si viene del relayoutData, detectar interacción
        if triggered_id == 'brain_graph' and relayout_data:
            # ESTRATEGIA PROACTIVA: ANY relayout event = interacción
            # Esto incluye cambios de zoom, rotación, pan, etc.
            new_state = {
                'is_interacting': True,
                'last_interaction': current_time
            }
            print(f"📱 DETECCION PROACTIVA: Evento relayout - PAUSANDO por 2s")
            print(f"   → Eventos: {list(relayout_data.keys())}")
            return new_state
        
        # Si viene del timer, usar para auto-reset inteligente
        elif triggered_id == 'interaction_timer':
            if interaction_state.get('is_interacting', False):
                time_since_last = current_time - interaction_state.get('last_interaction', 0)
                
                # Auto-reset después de 2 segundos SIN nuevos eventos
                # Esto maneja cuando la interacción termina pero no hay mouseup
                if time_since_last > 2.0:
                    new_state = {
                        'is_interacting': False,
                        'last_interaction': interaction_state.get('last_interaction', 0)
                    }
                    print(f"🔄 AUTO-RESET: {time_since_last:.3f}s sin nuevos eventos - REANUDANDO")
                    return new_state
            
            # Mantener estado actual si no es momento de reset
            print(f"⏰ TIMER: Manteniendo estado - interactuando={interaction_state.get('is_interacting', False)}")
            return interaction_state
        
        # Mantener estado actual
        return interaction_state

    @app.callback(
        [Output('brain_graph', 'figure'),
         Output('brain_camera_store', 'data')],
        [Input('timer', 'n_intervals'),
         Input('memory', 'data'),
         Input('sensor_select', 'value'),
         Input('quantity_select', 'value')],
        [State('brain_camera_store', 'data'),
         State('brain_interaction_store', 'data')]
    )
    def update_brain_visualization(n_intervals, data, selected_sensor, quantity_mode, camera_state, interaction_state):
        """
        Callback principal para actualizar la visualización del cerebro 3D.
        ESTRATEGIA: Pausa mientras is_interacting=True (controlado por mousedown/mouseup)
        con auto-reset de seguridad después de 1s sin eventos de cámara.
        """
        import time
        
        # Debug simplificado
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # VERIFICACION SIMPLIFICADA: Solo verificar el flag actual sin auto-reset
        current_time = time.time()
        should_pause = False
        
        if interaction_state:
            is_interacting_flag = interaction_state.get('is_interacting', False)
            last_interaction = interaction_state.get('last_interaction', 0)
            
            # CAMBIO: Solo pausar si el flag está True, sin auto-reset por tiempo
            should_pause = is_interacting_flag
            
            print(f"🔄 CALLBACK: triggered={triggered_id}, flag_interactuando={is_interacting_flag}, pausar={should_pause}")
        else:
            print(f"🔄 CALLBACK: sin estado de interacción, continuar")
        
        # Pausar solo si hay interacción activa
        if should_pause and triggered_id in ['timer', 'memory']:
            print(f"🚫 PAUSADO - interacción activa")
            return no_update, camera_state
        
        if not data or 'uid' not in data:
            print(f"❌ No hay datos válidos")
            return go.Figure().add_annotation(
                text="Esperando datos de la sesión...",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            ), camera_state
        
        # Continuar con actualización normal
        try:
            session_uid = data['uid']
            
            print(f"🔄 PROCESANDO DATOS - uid: {session_uid}, modo: {quantity_mode}")
            
            # Obtener datos de sensores según el modo seleccionado
            if quantity_mode == 'todos':
                # Mostrar todos los sensores disponibles
                sensors_data = {k: v for k, v in data.items() if k != 'uid' and v is not None}
                sensors_data['uid'] = session_uid
            else:  # modo 'individual'
                # Usar solo el sensor seleccionado
                if selected_sensor in data:
                    sensors_data = {selected_sensor: data[selected_sensor], 'uid': session_uid}
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
            
            # Crear nueva figura con uirevision (mantiene automáticamente la cámara)
            print(f"🔄 Creando figura con {len(sensors_data)-1} sensores")
            new_figure = brain_viz.create_live_brain_figure(sensors_data)
            
            # CRUCIAL: Aplicar cámara guardada si existe (refuerzo adicional al uirevision)
            if camera_state and new_figure and 'layout' in new_figure:
                if 'scene' not in new_figure['layout']:
                    new_figure['layout']['scene'] = {}
                
                # Aplicar la cámara guardada como respaldo
                new_figure['layout']['scene']['camera'] = camera_state.copy()
                print(f"✅ Aplicada cámara guardada")
            
            print(f"✅ ACTUALIZACION BYPASS EXITOSA")
            return new_figure, camera_state
            
        except Exception as e:
            print(f"❌ Error en callback bypass: {e}")
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
        camera_data = None
        if 'scene.camera' in relayout_data:
            camera_data = relayout_data['scene.camera']
        elif 'scene' in relayout_data and 'camera' in relayout_data['scene']:
            camera_data = relayout_data['scene']['camera']
        
        if camera_data:
            return camera_data
        
        return current_state