"""
Callbacks para actualizaciones de visualización del cerebro en vivo.
"""

from dash import Input, Output, State, callback
from src.py.brain_viz.brain_visualizer import brain_viz

@callback(
    Output("brain_graph", "figure"),
    Input("memory", "data"),
    State('quantity_select', 'value'),
    State('sensor_select', 'value'),
    prevent_initial_call=True
)
def update_brain_visualization(data, quantity_mode, selected_sensor):
    """
    Actualizar la visualización del cerebro con datos EEG en vivo.
    - Modo "individual": Muestra solo la región del cerebro del sensor seleccionado
    - Modo "todos": Muestra las regiones del cerebro de todos los sensores simultáneamente
    
    Parámetros:
    - data: Datos EEG actuales de todos los sensores
    - quantity_mode: "individual" o "todos"
    - selected_sensor: Sensor actualmente seleccionado (solo usado en modo individual)
    
    Retorna:
    - plotly.graph_objects.Figure: Figura del cerebro actualizada
    """
    if not data:
        # Retornar figura del cerebro por defecto si no hay datos
        return brain_viz.create_brain_figure()
    
    if quantity_mode == "individual":
        # Mostrar solo la región del sensor seleccionado
        if selected_sensor in data:
            sensor_data = {selected_sensor: data[selected_sensor], 'uid': data.get('uid', '')}
            updated_figure = brain_viz.create_live_brain_figure(sensor_data)
        else:
            updated_figure = brain_viz.create_brain_figure()
    else:  # quantity_mode == "todos"
        # Mostrar las regiones de todos los sensores
        updated_figure = brain_viz.create_live_brain_figure(data)
    
    return updated_figure