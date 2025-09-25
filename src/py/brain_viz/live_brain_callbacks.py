"""
Callbacks for live brain visualization updates.
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
    Update the brain visualization with live EEG data.
    - Mode "individual": Shows only the selected sensor's brain region
    - Mode "todos": Shows all sensors' brain regions simultaneously
    
    Parameters:
    - data: Current EEG data from all sensors
    - quantity_mode: "individual" or "todos"
    - selected_sensor: Currently selected sensor (only used in individual mode)
    
    Returns:
    - plotly.graph_objects.Figure: Updated brain figure
    """
    if not data:
        # Return default brain figure if no data
        return brain_viz.create_brain_figure()
    
    if quantity_mode == "individual":
        # Show only the selected sensor's region
        if selected_sensor in data:
            sensor_data = {selected_sensor: data[selected_sensor], 'uid': data.get('uid', '')}
            updated_figure = brain_viz.create_live_brain_figure(sensor_data)
        else:
            updated_figure = brain_viz.create_brain_figure()
    else:  # quantity_mode == "todos"
        # Show all sensors' regions
        updated_figure = brain_viz.create_live_brain_figure(data)
    
    return updated_figure