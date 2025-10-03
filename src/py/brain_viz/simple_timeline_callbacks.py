"""
Callbacks simplificados para el nuevo timeline.
Enfoque más directo y robusto usando extendData.
"""

import time
from dash import Input, Output, State, no_update, ctx, html
import plotly.graph_objects as go

def register_simple_timeline_callbacks(app):
    """Registrar callbacks del timeline simplificado."""
    
    # 1. Callback para actualizar datos de la sesión
    @app.callback(
        Output('simple_session_data', 'data'),
        [Input('memory', 'data'),
         Input('simple_timeline_reset_btn', 'n_clicks')],
        [State('simple_session_data', 'data'),
         State('simple_timeline_mode', 'data')],
        prevent_initial_call=True
    )
    def update_session_data(memory_data, reset_clicks, session_data, mode_data):
        """Actualizar los datos de la sesión actual."""
        
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # Reset del timeline
        if triggered_id == 'simple_timeline_reset_btn':
            print("🔄 RESET TIMELINE")
            return {
                'timestamps': [],
                'attention': [],
                'meditation': [],
                'signal_strength': [],
                'full_history': [],
                'session_start': time.time(),
                'max_points': 120
            }
        
        # Actualizar con nuevos datos solo si estamos en modo live
        if not memory_data or 'uid' not in memory_data:
            return session_data
            
        # Solo actualizar si estamos en modo live
        if mode_data and mode_data.get('mode') != 'live':
            return session_data
        
        # Inicializar si es necesario
        if not session_data or not session_data.get('session_start'):
            session_data = {
                'timestamps': [],
                'attention': [],
                'meditation': [],
                'signal_strength': [],
                'full_history': [],
                'session_start': time.time(),
                'max_points': 120
            }
        
        # Calcular tiempo relativo
        current_time = time.time() - session_data['session_start']
        
        # Extraer y promediar datos de todos los sensores
        all_attention = []
        all_meditation = []
        all_signal = []
        
        for sensor_key, sensor_data in memory_data.items():
            if sensor_key != 'uid' and sensor_data:
                all_attention.append(sensor_data.get('attention', 0))
                all_meditation.append(sensor_data.get('meditation', 0))
                all_signal.append(sensor_data.get('signal_strength', 0))
        
        # Calcular promedios
        avg_attention = sum(all_attention) / len(all_attention) if all_attention else 0
        avg_meditation = sum(all_meditation) / len(all_meditation) if all_meditation else 0
        avg_signal = sum(all_signal) / len(all_signal) if all_signal else 0
        
        # Agregar nuevos datos
        session_data['timestamps'].append(current_time)
        session_data['attention'].append(avg_attention)
        session_data['meditation'].append(avg_meditation)
        session_data['signal_strength'].append(avg_signal)
        session_data['full_history'].append(memory_data.copy())
        
        # Limitar cantidad de puntos (mantener últimos max_points)
        max_points = session_data.get('max_points', 120)
        if len(session_data['timestamps']) > max_points:
            session_data['timestamps'] = session_data['timestamps'][-max_points:]
            session_data['attention'] = session_data['attention'][-max_points:]
            session_data['meditation'] = session_data['meditation'][-max_points:]
            session_data['signal_strength'] = session_data['signal_strength'][-max_points:]
            session_data['full_history'] = session_data['full_history'][-max_points:]
        
        print(f"📊 TIMELINE: {len(session_data['timestamps'])} puntos, tiempo={current_time:.1f}s, "
              f"valores=[A:{avg_attention:.1f}, M:{avg_meditation:.1f}, S:{avg_signal:.1f}]")
        
        return session_data
    
    # 2. Callback para actualizar el gráfico con extendData
    @app.callback(
        Output('simple_timeline_graph', 'extendData'),
        [Input('simple_session_data', 'data')],
        [State('simple_timeline_mode', 'data')],
        prevent_initial_call=True
    )
    def update_timeline_graph(session_data, mode_data):
        """Actualizar gráfico del timeline usando extendData."""
        
        if not session_data or not session_data.get('timestamps'):
            return no_update
        
        # Solo extender datos si estamos en modo live
        if mode_data and mode_data.get('mode') != 'live':
            return no_update
        
        # Obtener último punto de datos
        if len(session_data['timestamps']) == 0:
            return no_update
            
        last_time = session_data['timestamps'][-1]
        last_attention = session_data['attention'][-1]
        last_meditation = session_data['meditation'][-1]
        last_signal = session_data['signal_strength'][-1]
        
        # Retornar datos para extender (orden: attention, meditation, signal)
        extend_data = {
            'x': [[last_time], [last_time], [last_time]],
            'y': [[last_attention], [last_meditation], [last_signal]]
        }
        
        # Limitar cantidad de puntos visibles (últimos 60 puntos = 1 minuto)
        trace_indices = [0, 1, 2]
        max_visible = 60
        
        return [extend_data, trace_indices, max_visible]
    
    # 3. Callback para manejar clicks y controles
    @app.callback(
        [Output('simple_timeline_mode', 'data'),
         Output('simple_timeline_status_badge', 'children'),
         Output('simple_timeline_status_badge', 'color')],
        [Input('simple_timeline_graph', 'clickData'),
         Input('simple_timeline_pause_btn', 'n_clicks'),
         Input('simple_timeline_resume_btn', 'n_clicks')],
        [State('simple_timeline_mode', 'data'),
         State('simple_session_data', 'data')],
        prevent_initial_call=True
    )
    def handle_timeline_controls(click_data, pause_clicks, resume_clicks, 
                                mode_data, session_data):
        """Manejar clicks en el timeline y botones de control."""
        
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        if not mode_data:
            mode_data = {'mode': 'live', 'selected_time': None, 'selected_data': None}
        
        new_mode = mode_data.copy()
        
        if triggered_id == 'simple_timeline_graph' and click_data:
            # Click en el gráfico - modo histórico
            selected_time = click_data['points'][0]['x']
            
            # Buscar datos más cercanos
            selected_data = None
            if session_data and session_data.get('timestamps'):
                timestamps = session_data['timestamps']
                closest_idx = min(range(len(timestamps)), 
                                 key=lambda i: abs(timestamps[i] - selected_time))
                selected_data = session_data['full_history'][closest_idx]
            
            new_mode.update({
                'mode': 'historical',
                'selected_time': selected_time,
                'selected_data': selected_data
            })
            
            status_text = f"🕒 HISTÓRICO: {selected_time:.1f}s"
            status_color = "warning"
            
            print(f"📍 CLICK TIMELINE: t={selected_time:.1f}s -> MODO HISTÓRICO")
            
        elif triggered_id == 'simple_timeline_pause_btn':
            # Pausar
            new_mode.update({
                'mode': 'paused',
                'selected_time': None,
                'selected_data': None
            })
            status_text = "⏸️ PAUSADO"
            status_color = "secondary"
            
            print("⏸️ TIMELINE PAUSADO")
            
        elif triggered_id == 'simple_timeline_resume_btn':
            # Reanudar
            new_mode.update({
                'mode': 'live',
                'selected_time': None,
                'selected_data': None
            })
            status_text = "🔴 EN VIVO"
            status_color = "success"
            
            print("▶️ TIMELINE REANUDADO")
            
        else:
            # Mantener estado actual
            if new_mode.get('mode') == 'live':
                status_text = "🔴 EN VIVO"
                status_color = "success"
            elif new_mode.get('mode') == 'historical':
                selected_time = new_mode.get('selected_time', 0)
                status_text = f"🕒 HISTÓRICO: {selected_time:.1f}s"
                status_color = "warning"
            else:  # paused
                status_text = "⏸️ PAUSADO"
                status_color = "secondary"
        
        return new_mode, status_text, status_color
    
    # 4. Callback para mostrar línea vertical en punto seleccionado
    @app.callback(
        Output('simple_timeline_graph', 'figure'),
        [Input('simple_timeline_mode', 'data')],
        [State('simple_timeline_graph', 'figure'),
         State('simple_session_data', 'data')],
        prevent_initial_call=True
    )
    def update_timeline_marker(mode_data, current_figure, session_data):
        """Actualizar marcador de posición seleccionada."""
        
        if not current_figure or not mode_data:
            return no_update
        
        # Crear una copia de la figura
        fig = go.Figure(current_figure)
        
        # LIMPIAR todas las shapes (líneas verticales) existentes
        if 'shapes' in fig.layout:
            fig.layout.shapes = []
        
        # LIMPIAR todas las annotations existentes de marcadores
        if 'annotations' in fig.layout:
            # Mantener solo las annotations originales (no las de marcadores)
            fig.layout.annotations = [
                ann for ann in fig.layout.annotations 
                if ann.text != "📍"
            ]
        
        # Agregar marcador SOLO si estamos en modo histórico
        if mode_data.get('mode') == 'historical' and mode_data.get('selected_time') is not None:
            selected_time = mode_data['selected_time']
            
            print(f"📍 Agregando marcador en t={selected_time:.1f}s")
            
            fig.add_vline(
                x=selected_time,
                line_dash="dash",
                line_color="red",
                line_width=3,
                annotation_text="📍",
                annotation_position="top"
            )
        else:
            print(f"🧹 Limpiando marcadores (modo: {mode_data.get('mode')})")
        
        return fig