"""
Callbacks simplificados para actualizaciones de visualización del cerebro en vivo.
Usa uirevision de Plotly para preservar automáticamente la posición de la cámara.
"""

import plotly.graph_objects as go
from dash import Input, Output, State, no_update, ctx
from src.py.brain_viz.brain_visualizer import brain_viz


def register_brain_callbacks(app):
    """Registrar callbacks del cerebro con la aplicación Dash."""
    
    @app.callback(
        [Output('brain_graph', 'figure'),
         Output('brain_camera_store', 'data')],
        [Input('timer', 'n_intervals'),
         Input('memory', 'data'),
         Input('sensor_select', 'value'),
         Input('quantity_select', 'value')],
        [State('brain_camera_store', 'data')]
    )
    def update_brain_visualization(n_intervals, data, selected_sensor, quantity_mode, camera_state):
        """
        Callback principal para actualizar la visualización del cerebro 3D.
        Combina uirevision con preservación manual de cámara para máxima robustez.
        """
        
        # Detectar qué disparó el callback para optimizar actualizaciones
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        if not data or 'uid' not in data:
            return go.Figure().add_annotation(
                text="Esperando datos de la sesión...",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=16)
            ), camera_state
        
        try:
            session_uid = data['uid']
            
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
                    return go.Figure().add_annotation(
                        text=f"No hay datos para: {selected_sensor}",
                        xref="paper", yref="paper", x=0.5, y=0.5,
                        showarrow=False, font=dict(size=16)
                    ), camera_state
            
            if len(sensors_data) <= 1:  # Solo contiene 'uid'
                return go.Figure().add_annotation(
                    text="No hay datos de sensores disponibles",
                    xref="paper", yref="paper", x=0.5, y=0.5,
                    showarrow=False, font=dict(size=16)
                ), camera_state
            
            # Crear nueva figura con uirevision (mantiene automáticamente la cámara)
            new_figure = brain_viz.create_live_brain_figure(sensors_data)
            
            # CRUCIAL: Aplicar cámara guardada si existe (refuerzo adicional al uirevision)
            if camera_state and new_figure and 'layout' in new_figure:
                if 'scene' not in new_figure['layout']:
                    new_figure['layout']['scene'] = {}
                
                # Aplicar la cámara guardada como respaldo
                new_figure['layout']['scene']['camera'] = camera_state.copy()
            
            return new_figure, camera_state
            
        except Exception as e:
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