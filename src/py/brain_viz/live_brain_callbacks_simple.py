"""
Callbacks simplificados para actualizaciones de visualización del cerebro en vivo.
Usa uirevision de Plotly para preservar automáticamente la posición de la cámara.
Incluye funcionalidad para pausar actualizaciones durante click presionado del mouse.
"""

import plotly.graph_objects as go
import time
from dash import Input, Output, State, no_update, ctx, ClientsideFunction
from src.py.brain_viz.brain_visualizer import brain_viz


def register_brain_callbacks(app):
    """Registrar callbacks del cerebro con la aplicación Dash."""
    
    # SOLUCION: ClientsideCallback simplificado y más robusto
    app.clientside_callback(
        """
        function(n_intervals) {
            try {
                // Verificar si existe el estado global
                if (typeof window.brainInteractionState === 'undefined') {
                    window.brainInteractionState = {
                        isInteracting: false,
                        lastInteraction: 0,
                        listenersInstalled: false
                    };
                }
                
                // Solo intentar instalar listeners si la gráfica existe
                const graph = document.getElementById('brain_graph');
                if (graph && !window.brainInteractionState.listenersInstalled) {
                    const canvas = graph.querySelector('canvas');
                    if (canvas) {
                        console.log('🖱️ Instalando listeners de mouse');
                        
                        canvas.addEventListener('mousedown', function() {
                            console.log('🖱️ MOUSEDOWN detectado');
                            window.brainInteractionState.isInteracting = true;
                            window.brainInteractionState.lastInteraction = Date.now() / 1000;
                        });
                        
                        canvas.addEventListener('mouseup', function() {
                            console.log('🖱️ MOUSEUP detectado');
                            window.brainInteractionState.isInteracting = false;
                        });
                        
                        window.brainInteractionState.listenersInstalled = true;
                    }
                }
                
                // Retornar el estado actual
                return {
                    is_interacting: window.brainInteractionState.isInteracting,
                    last_interaction: window.brainInteractionState.lastInteraction
                };
                
            } catch (error) {
                console.error('Error en ClientsideCallback:', error);
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
        HIBRIDO: Combinar detección por relayoutData con auto-reset por timer.
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
            camera_events = ['scene.camera']
            is_camera_event = any(key.startswith(event) for event in camera_events for key in relayout_data.keys())
            
            if is_camera_event:
                # TRUCO: Marcar como interactuando por UN BREVE MOMENTO
                new_state = {
                    'is_interacting': True,
                    'last_interaction': current_time
                }
                print(f"📱 DETECCION HIBRIDA: Interacción iniciada temporalmente")
                return new_state
        
        # Si viene del timer, verificar auto-reset
        elif triggered_id == 'interaction_timer':
            if interaction_state.get('is_interacting', False):
                time_since_last = current_time - interaction_state.get('last_interaction', 0)
                
                # Auto-reset después de 800ms (corto pero suficiente para pausar)
                if time_since_last > 0.8:
                    new_state = {
                        'is_interacting': False,
                        'last_interaction': interaction_state.get('last_interaction', 0)
                    }
                    print(f"🔄 AUTO-RESET HIBRIDO: {time_since_last:.3f}s sin interacción")
                    return new_state
        
        # Mantener estado actual
        return interaction_state
        camera_events = ['scene.camera']  # Solo cambios directos de cámara
        is_camera_event = any(key.startswith(event) for event in camera_events for key in relayout_data.keys())
        
        print(f"📱 DETECTAR INTERACCION: eventos={list(relayout_data.keys())}, es_camara={is_camera_event}")
        
        if is_camera_event:
            new_state = {
                'is_interacting': True,
                'last_interaction': current_time
            }
            print(f"   → INTERACCION INICIADA: {new_state}")
            return new_state
        
        current_state = interaction_state or {'is_interacting': False, 'last_interaction': 0}
        
        # Auto-reset del flag si ha pasado mucho tiempo sin nuevas interacciones
        if current_state.get('is_interacting', False):
            time_since_last = current_time - current_state.get('last_interaction', 0)
            if time_since_last > 2.0:  # 2 segundos sin nueva interacción = auto-reset
                current_state = {'is_interacting': False, 'last_interaction': current_state.get('last_interaction', 0)}
                print(f"   → AUTO-RESET: {time_since_last:.1f}s sin interacción, flag a False")
        
        print(f"   → Sin interacción nueva, manteniendo: {current_state}")
        return current_state
        # """
        # Verificar si la interacción ha terminado y forzar actualización si es necesario.
        # COMENTADO: Tiene bugs de propagación de estado en Dash
        # """
        # import time
        
        # if not interaction_state:
        #     return {'is_interacting': False, 'last_interaction': 0}, no_update
        
        # current_time = time.time()
        # last_interaction = interaction_state.get('last_interaction', 0)
        # is_currently_interacting = interaction_state.get('is_interacting', False)
        
        # print(f"⏰ TIMER CHECK: interactuando={is_currently_interacting}, última_interacción={last_interaction}, tiempo_actual={current_time}")
        
        # if not is_currently_interacting:
        #     print(f"   → NO está interactuando, sin cambios")
        #     return interaction_state, no_update
        
        # # Si han pasado más de 400ms sin eventos, la interacción terminó
        # time_since_last = current_time - last_interaction
        # print(f"   → Tiempo transcurrido: {time_since_last:.3f}s")
        
        # if time_since_last > 0.4:
        #     print(f"🔄 INTERACCIÓN TERMINADA - Forzando actualización desde timer")
        #     return new_state, new_figure
        # else:
        #     print(f"   → Aún interactuando, esperando...")
        
        # return interaction_state, no_update
        pass

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
        SOLUCION BYPASS: Verifica directamente el tiempo transcurrido en lugar de confiar en el estado.
        """
        import time
        
        # Debug simplificado
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # VERIFICACION CON AUTO-RESET: El callback principal también debe poder resetear el flag
        current_time = time.time()
        should_pause = False
        updated_interaction_state = interaction_state
        
        if interaction_state:
            is_interacting_flag = interaction_state.get('is_interacting', False)
            last_interaction = interaction_state.get('last_interaction', 0)
            time_since_last = current_time - last_interaction
            
            # Auto-reset aquí también si ha pasado demasiado tiempo
            if is_interacting_flag and time_since_last > 2.0:
                print(f"🔄 AUTO-RESET EN CALLBACK: {time_since_last:.1f}s sin interacción, reseteando flag")
                updated_interaction_state = {'is_interacting': False, 'last_interaction': last_interaction}
                is_interacting_flag = False
            
            # PAUSA MENOS AGRESIVA: Solo si el flag está True Y han pasado menos de 1.5 segundos
            should_pause = is_interacting_flag and time_since_last < 1.5
            
            print(f"🔄 CALLBACK BYPASS: triggered={triggered_id}, flag_interactuando={is_interacting_flag}, hace={time_since_last:.3f}s, pausar={should_pause}")
        else:
            print(f"🔄 CALLBACK BYPASS: sin estado de interacción, continuar")
        
        # Pausar solo si hay interacción activa y reciente
        if should_pause and triggered_id in ['timer', 'memory']:
            print(f"🚫 PAUSADO - interacción activa reciente")
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