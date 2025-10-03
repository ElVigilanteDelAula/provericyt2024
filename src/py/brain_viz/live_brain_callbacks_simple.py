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
         Input('quantity_select', 'value'),
         Input('simple_timeline_mode', 'data')],  # Usar el nuevo timeline simplificado
        [State('brain_camera_store', 'data'),
         State('brain_interaction_store', 'data')]
    )
    def update_brain_visualization(n_intervals, data, selected_sensor, quantity_mode, 
                                  timeline_mode, camera_state, interaction_state):
        """
        Callback principal para actualizar la visualización del cerebro 3D.
        ESTRATEGIA: Pausa mientras is_interacting=True O cuando timeline está en modo histórico/pausado.
        """
        import time
        
        # Debug simplificado
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # VERIFICACION DE TIMELINE: Pausar si no estamos en modo 'live'
        timeline_mode = 'live'
        historical_data = None
        
        if timeline_state:
            timeline_mode = timeline_state.get('mode', 'live')
            
            # Si estamos en modo histórico, obtener los datos del punto seleccionado
            if timeline_mode == 'historical':
                selected_time = timeline_state.get('selected_time')
                if selected_time is not None and history_state and history_state.get('data_points'):
                    # Encontrar el punto de datos más cercano al tiempo seleccionado
                    timestamps = history_state.get('timestamps', [])
                    data_points = history_state.get('data_points', [])
                    
                    if timestamps and data_points:
                        closest_idx = min(range(len(timestamps)), 
                                         key=lambda i: abs(timestamps[i] - selected_time))
                        historical_data = data_points[closest_idx]['full_data']
                        
                        print(f"🕒 MODO HISTÓRICO: Mostrando datos de t={selected_time:.1f}s (idx={closest_idx})")
        
        # VERIFICACION SIMPLIFICADA: Solo verificar el flag actual sin auto-reset
        current_time = time.time()
        should_pause = False
        
        if interaction_state:
            is_interacting_flag = interaction_state.get('is_interacting', False)
            last_interaction = interaction_state.get('last_interaction', 0)
            
            # CAMBIO: Solo pausar si el flag está True, sin auto-reset por tiempo
            should_pause = is_interacting_flag
            
            print(f"🔄 CALLBACK: triggered={triggered_id}, timeline_mode={timeline_mode}, flag_interactuando={is_interacting_flag}, pausar={should_pause}")
        else:
            print(f"🔄 CALLBACK: timeline_mode={timeline_mode}, sin estado de interacción")
        
        # Pausar solo si hay interacción activa Y estamos en modo live
        if should_pause and triggered_id in ['timer', 'memory'] and timeline_mode == 'live':
            print(f"🚫 PAUSADO - interacción activa en modo live")
            return no_update, no_update
        
        # Pausar si estamos en modo pausado
        if timeline_mode == 'paused' and triggered_id in ['timer', 'memory']:
            print(f"⏸️ PAUSADO - modo pausado del timeline")
            return no_update, no_update
        
        # Determinar qué datos usar
        display_data = historical_data if historical_data else data
        
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
            
            print(f"🔄 PROCESANDO DATOS - uid: {session_uid}, modo: {quantity_mode}, timeline: {timeline_mode}")
            
            # Obtener datos de sensores según el modo seleccionado
            if quantity_mode == 'todos':
                # Mostrar todos los sensores disponibles
                sensors_data = {k: v for k, v in display_data.items() if k != 'uid' and v is not None}
                sensors_data['uid'] = session_uid
                mode_title = "Todos los sensores"
            else:  # modo 'individual'
                # Usar solo el sensor seleccionado
                if selected_sensor in display_data:
                    sensors_data = {selected_sensor: display_data[selected_sensor], 'uid': session_uid}
                    mode_title = f"Sensor: {selected_sensor}"
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
            
            # Obtener estado de cámara para preservar la vista
            camera_settings = camera_state.get('camera') if camera_state else None
            
            # Crear nueva figura del cerebro con los datos actuales
            print(f"🔄 Creando figura con {len(sensors_data)-1} sensores")
            new_figure = brain_viz.create_live_brain_figure(sensors_data)
            
            # Agregar indicador del modo timeline al título
            if timeline_mode == 'historical':
                selected_time = timeline_state.get('selected_time', 0)
                current_title = new_figure.layout.title.text if new_figure.layout.title else "Visualización Cerebro 3D"
                new_figure.update_layout(
                    title=f"{current_title}<br><span style='color: orange; font-size: 12px;'>🕒 Modo Histórico: t={selected_time:.1f}s</span>"
                )
            elif timeline_mode == 'paused':
                current_title = new_figure.layout.title.text if new_figure.layout.title else "Visualización Cerebro 3D"
                new_figure.update_layout(
                    title=f"{current_title}<br><span style='color: gray; font-size: 12px;'>⏸️ Pausado</span>"
                )
            
            # CRUCIAL: Aplicar cámara guardada si existe (refuerzo adicional al uirevision)
            if camera_state and new_figure and 'layout' in new_figure:
                if 'scene' not in new_figure['layout']:
                    new_figure['layout']['scene'] = {}
                
                # Aplicar la cámara guardada como respaldo
                if 'camera' in camera_state:
                    new_figure['layout']['scene']['camera'] = camera_state['camera'].copy()
                    print(f"✅ Aplicada cámara guardada")
                elif camera_settings:
                    new_figure['layout']['scene']['camera'] = camera_settings.copy()
                    print(f"✅ Aplicada cámara desde settings")
            
            print(f"✅ CEREBRO ACTUALIZADO: modo={timeline_mode}, sensores={len(sensors_data)-1}, uid={session_uid}")
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

    # ========================================================================================
    # TIMELINE CALLBACKS - Navegación temporal y control de historial
    # ========================================================================================
    
    @app.callback(
        [Output('session_history_store', 'data'),
         Output('timeline_state_store', 'data', allow_duplicate=True)],
        [Input('memory', 'data'),
         Input('timer', 'n_intervals')],
        [State('session_history_store', 'data'),
         State('timeline_state_store', 'data')],
        prevent_initial_call=True
    )
    def update_session_history(data, n_intervals, history_state, timeline_state):
        """
        Actualizar el historial de la sesión actual con nuevos datos.
        Solo guarda datos cuando estamos en modo 'live'.
        """
        if not data or 'uid' not in data:
            return history_state, timeline_state
        
        # Solo actualizar historial si estamos en modo 'live'
        if timeline_state.get('mode', 'live') != 'live':
            return history_state, timeline_state
        
        # Inicializar historial si es la primera vez
        if not history_state or 'timestamps' not in history_state:
            # Establecer el tiempo de inicio de la sesión
            timeline_state['session_start'] = time.time()
            history_state = {
                'timestamps': [],
                'data_points': [],
                'session_start': timeline_state['session_start']
            }
        
        # Calcular tiempo relativo desde el inicio de la sesión
        session_start = history_state.get('session_start', time.time())
        current_time = time.time() - session_start
        
        # Extraer datos relevantes para el timeline (promedio de todos los sensores)
        signal_strengths = []
        attentions = []
        meditations = []
        
        for sensor_key, sensor_data in data.items():
            if sensor_key != 'uid' and sensor_data:
                signal_strengths.append(sensor_data.get('signal_strength', 0))
                attentions.append(sensor_data.get('attention', 0))
                meditations.append(sensor_data.get('meditation', 0))
        
        # Calcular promedios
        avg_signal = sum(signal_strengths) / len(signal_strengths) if signal_strengths else 0
        avg_attention = sum(attentions) / len(attentions) if attentions else 0
        avg_meditation = sum(meditations) / len(meditations) if meditations else 0
        
        # Debug: Mostrar los valores que se están guardando
        print(f"🔍 NUEVOS VALORES: signal={avg_signal:.1f}, attention={avg_attention:.1f}, meditation={avg_meditation:.1f}, tiempo={current_time:.1f}s")
        
        # Agregar punto al historial
        history_state['timestamps'].append(current_time)
        history_state['data_points'].append({
            'signal_strength': avg_signal,
            'attention': avg_attention,
            'meditation': avg_meditation,
            'full_data': data.copy()  # Guardar todos los datos para recuperación posterior
        })
        
        # Limitar el historial a los últimos 300 puntos (5 minutos)
        if len(history_state['timestamps']) > 300:
            history_state['timestamps'] = history_state['timestamps'][-300:]
            history_state['data_points'] = history_state['data_points'][-300:]
        
        print(f"📊 HISTORIAL: {len(history_state['timestamps'])} puntos, tiempo={current_time:.1f}s")
        
        return history_state, timeline_state
    
    @app.callback(
        Output('timeline_graph', 'figure'),
        [Input('session_history_store', 'data'),
         Input('timeline_state_store', 'data')],
        prevent_initial_call=True
    )
    def update_timeline_graph(history_state, timeline_state):
        """
        Actualizar la gráfica del timeline con los datos del historial.
        """
        print(f"🔄 ACTUALIZANDO TIMELINE: history_state={bool(history_state)}")
        
        if not history_state or not history_state.get('timestamps'):
            print("📊 Timeline vacío - creando figura inicial")
            # Timeline vacío
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='Signal Strength', 
                                   line=dict(color='#1f77b4', width=2)))
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='Attention', 
                                   line=dict(color='#ff7f0e', width=2)))
            fig.add_trace(go.Scatter(x=[], y=[], mode='lines+markers', name='Meditation', 
                                   line=dict(color='#2ca02c', width=2)))
        else:
            timestamps = history_state['timestamps']
            data_points = history_state['data_points']
            
            print(f"📊 Datos del timeline: {len(timestamps)} puntos, rango tiempo: {min(timestamps):.1f}-{max(timestamps):.1f}s")
            
            # Extraer series de datos
            signal_values = [point['signal_strength'] for point in data_points]
            attention_values = [point['attention'] for point in data_points]
            meditation_values = [point['meditation'] for point in data_points]
            
            # Debug más detallado
            print(f"📊 Rangos de valores:")
            print(f"    Signal: {min(signal_values):.1f}-{max(signal_values):.1f}")
            print(f"    Attention: {min(attention_values):.1f}-{max(attention_values):.1f}")
            print(f"    Meditation: {min(meditation_values):.1f}-{max(meditation_values):.1f}")
            print(f"📊 Últimos 3 valores:")
            print(f"    Timestamps: {timestamps[-3:] if len(timestamps) >= 3 else timestamps}")
            print(f"    Signal: {signal_values[-3:] if len(signal_values) >= 3 else signal_values}")
            print(f"    Attention: {attention_values[-3:] if len(attention_values) >= 3 else attention_values}")
            print(f"    Meditation: {meditation_values[-3:] if len(meditation_values) >= 3 else meditation_values}")
            
            # Crear figura COMPLETAMENTE NUEVA cada vez
            fig = go.Figure()
            
            fig.add_trace(create_timeline_data_trace(
                timestamps, signal_values, 'Signal Strength', '#1f77b4'
            ))
            fig.add_trace(create_timeline_data_trace(
                timestamps, attention_values, 'Attention', '#ff7f0e'
            ))
            fig.add_trace(create_timeline_data_trace(
                timestamps, meditation_values, 'Meditation', '#2ca02c'
            ))
            
            # Marcar punto seleccionado si existe
            selected_time = timeline_state.get('selected_time')
            if selected_time is not None and timestamps:
                # Encontrar el punto más cercano
                closest_idx = min(range(len(timestamps)), 
                                 key=lambda i: abs(timestamps[i] - selected_time))
                
                # Agregar marcador vertical
                fig.add_vline(
                    x=selected_time,
                    line_dash="dash",
                    line_color="red",
                    line_width=2,
                    annotation_text="📍 Seleccionado",
                    annotation_position="top"
                )
        
        # Configurar layout
        fig.update_layout(
            title="Timeline de Activación - Sesión Actual",
            xaxis_title="Tiempo (segundos)",
            yaxis_title="Activación (%)",
            height=300,
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode='x unified',
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor='rgba(240,240,240,0.8)',
            paper_bgcolor='white',
            yaxis=dict(range=[0, 100]),
            xaxis=dict(type='linear')  # Asegurar que X sea lineal
        )
        
        return fig
    
    @app.callback(
        [Output('timeline_state_store', 'data', allow_duplicate=True),
         Output('timeline_status', 'children'),
         Output('timeline_status', 'color'),
         Output('timeline_pause_btn', 'disabled'),
         Output('timeline_resume_btn', 'disabled')],
        [Input('timeline_graph', 'clickData'),
         Input('timeline_pause_btn', 'n_clicks'),
         Input('timeline_resume_btn', 'n_clicks'),
         Input('timeline_reset_btn', 'n_clicks')],
        [State('timeline_state_store', 'data'),
         State('session_history_store', 'data')],
        prevent_initial_call=True
    )
    def handle_timeline_interaction(click_data, pause_clicks, resume_clicks, reset_clicks, 
                                   timeline_state, history_state):
        """
        Manejar interacciones con el timeline: clicks, botones de control.
        """
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        if not timeline_state:
            timeline_state = {'mode': 'live', 'selected_time': None}
        
        new_state = timeline_state.copy()
        
        if triggered_id == 'timeline_graph' and click_data:
            # Click en el timeline - cambiar a modo histórico
            selected_time = click_data['points'][0]['x']
            new_state.update({
                'mode': 'historical',
                'selected_time': selected_time
            })
            status_text = [html.Strong("🕒 MODO HISTÓRICO"), f" - Mostrando datos de t={selected_time:.1f}s"]
            status_color = "warning"
            pause_disabled = True
            resume_disabled = False
            
            print(f"📍 TIMELINE CLICK: Seleccionado tiempo {selected_time:.1f}s - PAUSANDO actualizaciones")
        
        elif triggered_id == 'timeline_pause_btn':
            # Botón pausar - pausar en tiempo actual
            new_state.update({
                'mode': 'paused',
                'selected_time': None
            })
            status_text = [html.Strong("⏸️ PAUSADO"), " - Actualizaciones detenidas"]
            status_color = "secondary"
            pause_disabled = True
            resume_disabled = False
            
            print(f"⏸️ TIMELINE: PAUSADO manualmente")
        
        elif triggered_id == 'timeline_resume_btn':
            # Botón reanudar - volver a tiempo real
            new_state.update({
                'mode': 'live',
                'selected_time': None
            })
            status_text = [html.Strong("🔴 TIEMPO REAL"), " - Actualizaciones automáticas activas"]
            status_color = "success"
            pause_disabled = False
            resume_disabled = True
            
            print(f"▶️ TIMELINE: REANUDADO - volviendo a tiempo real")
        
        elif triggered_id == 'timeline_reset_btn':
            # Botón reset - limpiar timeline y volver a tiempo real
            new_state.update({
                'mode': 'live',
                'selected_time': None
            })
            status_text = [html.Strong("🔄 RESETEADO"), " - Timeline reiniciado"]
            status_color = "info"
            pause_disabled = False
            resume_disabled = True
            
            print(f"🔄 TIMELINE: RESETEADO")
        
        else:
            # Mantener estado actual
            if new_state.get('mode') == 'live':
                status_text = [html.Strong("🔴 TIEMPO REAL"), " - Actualizaciones automáticas activas"]
                status_color = "success"
                pause_disabled = False
                resume_disabled = True
            elif new_state.get('mode') == 'historical':
                selected_time = new_state.get('selected_time', 0)
                status_text = [html.Strong("🕒 MODO HISTÓRICO"), f" - Mostrando datos de t={selected_time:.1f}s"]
                status_color = "warning"
                pause_disabled = True
                resume_disabled = False
            else:  # paused
                status_text = [html.Strong("⏸️ PAUSADO"), " - Actualizaciones detenidas"]
                status_color = "secondary"
                pause_disabled = True
                resume_disabled = False
        
        return new_state, status_text, status_color, pause_disabled, resume_disabled

    @app.callback(
        Output('session_history_store', 'data', allow_duplicate=True),
        [Input('timeline_reset_btn', 'n_clicks')],
        prevent_initial_call=True
    )
    def reset_session_history(reset_clicks):
        """
        Resetear el historial de la sesión cuando se presiona el botón reset.
        """
        print("🔄 RESETEANDO HISTORIAL DEL TIMELINE")
        
        # Reinicializar completamente el historial
        return {
            'timestamps': [],
            'data_points': [],
            'session_start': time.time()
        }