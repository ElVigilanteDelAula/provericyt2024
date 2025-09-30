"""
Callbacks para actualizaciones de visualización del cerebro en vivo.
"""

from dash import Input, Output, State, callback, no_update, Patch, ctx
from src.py.brain_viz.brain_visualizer import brain_viz

@callback(
    Output('brain_camera_store', 'data', allow_duplicate=True),
    Input('brain_graph', 'relayoutData'),
    State('brain_camera_store', 'data'),
    prevent_initial_call=True
)
def store_brain_camera_state(relayout_data, current_camera_state):
    """
    Capturar y almacenar cambios en la posición de la cámara del cerebro 3D.
    
    Parámetros:
    - relayout_data: Datos de cambios de layout del gráfico (incluye cámara)
    - current_camera_state: Estado actual almacenado de la cámara
    
    Retorna:
    - dict: Estado actualizado de la cámara
    """
    if not relayout_data:
        return no_update
    
    # Buscar cambios en la configuración de la cámara
    updated_camera = current_camera_state.copy() if current_camera_state else {}
    
    # Extraer configuración de la cámara si está presente
    scene_keys = [key for key in relayout_data.keys() if key.startswith('scene.camera')]
    
    if scene_keys:
        # Actualizar configuración de cámara
        for key in scene_keys:
            if key == 'scene.camera.eye.x':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['x'] = relayout_data[key]
            elif key == 'scene.camera.eye.y':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['y'] = relayout_data[key]
            elif key == 'scene.camera.eye.z':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['z'] = relayout_data[key]
            elif key == 'scene.camera.center.x':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['x'] = relayout_data[key]
            elif key == 'scene.camera.center.y':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['y'] = relayout_data[key]
            elif key == 'scene.camera.center.z':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['z'] = relayout_data[key]
            elif key == 'scene.camera.up.x':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['x'] = relayout_data[key]
            elif key == 'scene.camera.up.y':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['y'] = relayout_data[key]
            elif key == 'scene.camera.up.z':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['z'] = relayout_data[key]
        
        return updated_camera
    
    return no_update

"""
Callbacks para actualizaciones de visualización del cerebro en vivo.
"""

from dash import Input, Output, State, callback, no_update, Patch, ctx
from src.py.brain_viz.brain_visualizer import brain_viz

@callback(
    Output('brain_camera_store', 'data'),
    Input('brain_graph', 'relayoutData'),
    State('brain_camera_store', 'data'),
    prevent_initial_call=True
)
def store_brain_camera_state(relayout_data, current_camera_state):
    """
    Capturar y almacenar cambios en la posición de la cámara del cerebro 3D.
    
    Parámetros:
    - relayout_data: Datos de cambios de layout del gráfico (incluye cámara)
    - current_camera_state: Estado actual almacenado de la cámara
    
    Retorna:
    - dict: Estado actualizado de la cámara
    """
    if not relayout_data:
        return no_update
    
    # Buscar cambios en la configuración de la cámara
    updated_camera = current_camera_state.copy() if current_camera_state else {}
    
    # Extraer configuración de la cámara si está presente
    scene_keys = [key for key in relayout_data.keys() if key.startswith('scene.camera')]
    
    if scene_keys:
        # Actualizar configuración de cámara
        for key in scene_keys:
            if key == 'scene.camera.eye.x':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['x'] = relayout_data[key]
            elif key == 'scene.camera.eye.y':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['y'] = relayout_data[key]
            elif key == 'scene.camera.eye.z':
                if 'eye' not in updated_camera:
                    updated_camera['eye'] = {}
                updated_camera['eye']['z'] = relayout_data[key]
            elif key == 'scene.camera.center.x':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['x'] = relayout_data[key]
            elif key == 'scene.camera.center.y':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['y'] = relayout_data[key]
            elif key == 'scene.camera.center.z':
                if 'center' not in updated_camera:
                    updated_camera['center'] = {}
                updated_camera['center']['z'] = relayout_data[key]
            elif key == 'scene.camera.up.x':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['x'] = relayout_data[key]
            elif key == 'scene.camera.up.y':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['y'] = relayout_data[key]
            elif key == 'scene.camera.up.z':
                if 'up' not in updated_camera:
                    updated_camera['up'] = {}
                updated_camera['up']['z'] = relayout_data[key]
        
        return updated_camera
    
    return no_update

@callback(
    Output("brain_graph", "figure"),
    Input("memory", "data"),
    Input('quantity_select', 'value'),
    Input('sensor_select', 'value'),
    State('brain_camera_store', 'data'),
    State("brain_graph", "figure"),
    prevent_initial_call=True
)
def update_brain_visualization(data, quantity_mode, selected_sensor, camera_state, current_figure):
    """
    Actualizar la visualización del cerebro 3D preservando completamente la posición de la cámara.
    Distingue entre actualizaciones de datos vs cambios de configuración.
    
    Parámetros:
    - data: Datos EEG actuales de todos los sensores
    - quantity_mode: "individual" o "todos"
    - selected_sensor: Sensor actualmente seleccionado
    - camera_state: Estado guardado de la cámara
    - current_figure: Figura actual para verificar si existe
    
    Retorna:
    - plotly.graph_objects.Figure o Patch: Figura actualizada
    """
    if not data:
        return no_update
    
    # Detectar qué input disparó el callback
    triggered_id = ctx.triggered_id if ctx.triggered else None
    is_data_update = triggered_id == "memory"
    is_config_change = triggered_id in ["quantity_select", "sensor_select"]
    
    # Si no hay figura actual, crear una nueva (solo al inicio)
    if current_figure is None or not current_figure.get('data'):
        if quantity_mode == "individual":
            if selected_sensor in data:
                sensor_data = {selected_sensor: data[selected_sensor], 'uid': data.get('uid', '')}
                new_figure = brain_viz.create_live_brain_figure(sensor_data)
            else:
                new_figure = brain_viz.create_brain_figure()
        else:  # quantity_mode == "todos"
            new_figure = brain_viz.create_live_brain_figure(data)
        
        # Aplicar estado de cámara guardado si existe
        if camera_state and new_figure:
            if 'layout' not in new_figure:
                new_figure['layout'] = {}
            if 'scene' not in new_figure['layout']:
                new_figure['layout']['scene'] = {}
            new_figure['layout']['scene']['camera'] = camera_state
        
        return new_figure
    
    # Si es un cambio de configuración (sensor/modo), recrear figura con cámara preservada
    if is_config_change:
        print(f"🔄 CONFIG CHANGE: sensor={selected_sensor}, mode={quantity_mode}")
        print(f"📷 Camera state: {camera_state}")
        
        if quantity_mode == "individual":
            if selected_sensor in data:
                sensor_data = {selected_sensor: data[selected_sensor], 'uid': data.get('uid', '')}
                new_figure = brain_viz.create_live_brain_figure(sensor_data)
            else:
                return no_update
        else:  # quantity_mode == "todos"
            new_figure = brain_viz.create_live_brain_figure(data)
        
        # CRÍTICO: Aplicar estado de cámara guardado si existe
        if camera_state and new_figure:
            print(f"🎯 Applying saved camera state: {camera_state}")
            if 'layout' not in new_figure:
                new_figure['layout'] = {}
            if 'scene' not in new_figure['layout']:
                new_figure['layout']['scene'] = {}
            
            # Aplicar la cámara guardada
            new_figure['layout']['scene']['camera'] = camera_state.copy()
            
            # CLAVE: Usar uirevision para mantener la interacción del usuario
            new_figure['layout']['scene']['uirevision'] = 'brain_camera'
            new_figure['layout']['uirevision'] = 'brain_layout'
        else:
            print("⚠️ No camera state to apply or no figure created")
            # Incluso sin estado de cámara, usar uirevision
            if new_figure and 'layout' in new_figure:
                if 'scene' not in new_figure['layout']:
                    new_figure['layout']['scene'] = {}
                new_figure['layout']['scene']['uirevision'] = 'brain_camera'
                new_figure['layout']['uirevision'] = 'brain_layout'
        
        return new_figure
    
    # Si es solo actualización de datos, usar Patch sin tocar la cámara
    if is_data_update:
        # Determinar qué datos usar según el modo
        if quantity_mode == "individual":
            if selected_sensor in data:
                sensor_data = {selected_sensor: data[selected_sensor], 'uid': data.get('uid', '')}
            else:
                return no_update
        else:  # quantity_mode == "todos"
            sensor_data = data
        
        # Obtener nuevas intensidades
        intensity_update = brain_viz.update_live_brain_intensity(sensor_data)
        
        if intensity_update is None:
            return no_update
        
        # Usar Patch SOLO para actualizar intensidades, NO tocar la cámara
        patched_figure = Patch()
        
        try:
            # Actualizar intensidad del hemisferio derecho (trace 0)
            if 'intensity_right' in intensity_update:
                patched_figure['data'][0]['intensity'] = intensity_update['intensity_right']
            
            # Actualizar intensidad del hemisferio izquierdo (trace 1)  
            if 'intensity_left' in intensity_update:
                patched_figure['data'][1]['intensity'] = intensity_update['intensity_left']
            
            # IMPORTANTE: NO tocar la cámara en actualizaciones de datos
            # Esto permite que Plotly mantenga naturalmente la posición actual
                
        except (KeyError, IndexError, TypeError):
            # Si hay algún problema con el patch, no actualizar nada
            return no_update
        
        return patched_figure
    
    return no_update