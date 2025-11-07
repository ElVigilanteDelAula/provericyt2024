"""Callbacks simplificados para el timeline reducido del cerebro 3D."""

import time

import plotly.graph_objects as go
from dash import Input, Output, State, ctx, no_update

def register_simple_timeline_callbacks(app):
    """Registrar callbacks del timeline simplificado."""

    @app.callback(
        Output('simple_session_data', 'data'),
        [Input('memory', 'data'),
         Input('simple_timeline_reset_btn', 'n_clicks')],
        [State('simple_session_data', 'data'),
         State('simple_timeline_mode', 'data')],
        prevent_initial_call=True
    )
    def update_session_data(memory_data, _reset_clicks, session_data, mode_data):
        """Actualizar los datos de la sesión actual."""
        triggered_id = ctx.triggered_id if ctx.triggered else None

        if triggered_id == 'simple_timeline_reset_btn':
            return _fresh_session_state()

        if not memory_data or 'uid' not in memory_data:
            return session_data

        if mode_data and mode_data.get('mode') != 'live':
            return session_data

        session_data = session_data or _fresh_session_state()
        if not session_data.get('session_start'):
            session_data['session_start'] = time.time()

        _append_session_point(session_data, memory_data)
        _trim_session_history(session_data)
        return session_data

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
        
        if mode_data and mode_data.get('mode') != 'live':
            return no_update
        
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

        mode_data = mode_data or _default_timeline_mode()
        new_mode = mode_data.copy()

        if triggered_id == 'simple_timeline_graph' and click_data:
            selected_time = click_data['points'][0]['x']
            selected_data = _select_history_point(session_data, selected_time)
            new_mode.update({'mode': 'historical', 'selected_time': selected_time, 'selected_data': selected_data})
            status_text = f"🕒 HISTÓRICO: {selected_time:.1f}s"
            status_color = "warning"

        elif triggered_id == 'simple_timeline_pause_btn':
            new_mode.update({'mode': 'paused', 'selected_time': None, 'selected_data': None})
            status_text = "⏸️ PAUSADO"
            status_color = "secondary"

        elif triggered_id == 'simple_timeline_resume_btn':
            new_mode = _default_timeline_mode()
            status_text = "🔴 EN VIVO"
            status_color = "success"

        else:
            status_text, status_color = _status_badge(new_mode)
        
        return new_mode, status_text, status_color

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

        fig = go.Figure(current_figure)
        _clear_markers(fig)

        if mode_data.get('mode') == 'historical' and mode_data.get('selected_time') is not None:
            fig.add_vline(
                x=mode_data['selected_time'],
                line_dash="dash",
                line_color="red",
                line_width=3,
                annotation_text="📍",
                annotation_position="top"
            )

        return fig


def _fresh_session_state():
    return {
        'timestamps': [],
        'attention': [],
        'meditation': [],
        'signal_strength': [],
        'full_history': [],
        'session_start': time.time(),
        'max_points': 120
    }


def _append_session_point(session_data, memory_data):
    current_time = time.time() - session_data['session_start']
    attention, meditation, signal = _average_metrics(memory_data)

    session_data['timestamps'].append(current_time)
    session_data['attention'].append(attention)
    session_data['meditation'].append(meditation)
    session_data['signal_strength'].append(signal)
    session_data['full_history'].append(memory_data.copy())


def _average_metrics(memory_data):
    attentions, meditations, signals = [], [], []
    for sensor_key, sensor_data in memory_data.items():
        if sensor_key == 'uid' or not sensor_data:
            continue
        attentions.append(sensor_data.get('attention', 0))
        meditations.append(sensor_data.get('meditation', 0))
        signals.append(sensor_data.get('signal_strength', 0))

    avg = lambda items: sum(items) / len(items) if items else 0
    return avg(attentions), avg(meditations), avg(signals)


def _trim_session_history(session_data):
    max_points = session_data.get('max_points', 120)
    excess = len(session_data['timestamps']) - max_points
    if excess <= 0:
        return

    for key in ('timestamps', 'attention', 'meditation', 'signal_strength', 'full_history'):
        session_data[key] = session_data[key][-max_points:]


def _default_timeline_mode():
    return {'mode': 'live', 'selected_time': None, 'selected_data': None}


def _select_history_point(session_data, selected_time):
    if not session_data or not session_data.get('timestamps'):
        return None

    timestamps = session_data['timestamps']
    index = min(range(len(timestamps)), key=lambda i: abs(timestamps[i] - selected_time))
    return session_data['full_history'][index]


def _status_badge(mode_data):
    if mode_data.get('mode') == 'historical':
        selected_time = mode_data.get('selected_time', 0)
        return f"🕒 HISTÓRICO: {selected_time:.1f}s", "warning"
    if mode_data.get('mode') == 'paused':
        return "⏸️ PAUSADO", "secondary"
    return "🔴 EN VIVO", "success"


def _clear_markers(fig):
    if 'shapes' in fig.layout:
        fig.layout.shapes = []
    if 'annotations' in fig.layout:
        fig.layout.annotations = [ann for ann in fig.layout.annotations if ann.text != "📍"]