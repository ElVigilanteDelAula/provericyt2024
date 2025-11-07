"""Callbacks para actualizaciones de la visualización 3D del cerebro."""

import plotly.graph_objects as go
from dash import Input, Output, Patch, State, callback, ctx, no_update

from src.py.brain_viz.brain_visualizer import brain_viz


@callback(
    Output("brain_camera_store", "data", allow_duplicate=True),
    Input("brain_graph", "relayoutData"),
    State("brain_camera_store", "data"),
    prevent_initial_call=True,
)
def store_brain_camera_state(relayout_data, current_camera_state):
    """Persistir la posición actual de la cámara cada vez que el usuario interactúa."""
    if not relayout_data:
        return no_update

    camera_data = relayout_data.get("scene.camera")
    if not camera_data:
        camera_data = relayout_data.get("scene", {}).get("camera") if isinstance(relayout_data.get("scene"), dict) else None

    if not camera_data:
        return no_update

    packed = _pack_camera(camera_data)
    if packed == current_camera_state:
        return no_update

    return packed


@callback(
    Output("brain_graph", "figure"),
    Input("memory", "data"),
    Input("quantity_select", "value"),
    Input("sensor_select", "value"),
    State("brain_camera_store", "data"),
    State("brain_graph", "figure"),
    prevent_initial_call=True,
)
def update_brain_visualization(memory_data, quantity_mode, selected_sensor, camera_state, current_figure):
    """Actualizar la figura del cerebro preservando la cámara cuando sea posible."""
    if not memory_data:
        return no_update

    triggered_id = ctx.triggered_id or ""
    sensors_data = _build_sensor_payload(memory_data, quantity_mode, selected_sensor)
    if sensors_data is None:
        return no_update

    requires_rebuild = triggered_id in {"quantity_select", "sensor_select"} or not _figure_has_mesh(current_figure)

    if requires_rebuild:
        figure = brain_viz.create_live_brain_figure(sensors_data)
        _apply_camera(figure, camera_state)
        _insert_uirevision(figure)
        return figure

    if triggered_id == "memory":
        intensity_update = brain_viz.update_live_brain_intensity(sensors_data)
        if not intensity_update:
            return no_update

        patch = Patch()
        try:
            if "intensity_right" in intensity_update:
                patch["data"][0]["intensity"] = intensity_update["intensity_right"]
            if "intensity_left" in intensity_update:
                patch["data"][1]["intensity"] = intensity_update["intensity_left"]
        except (IndexError, KeyError, TypeError):
            return no_update

        return patch

    return no_update


def _pack_camera(camera):
    return {"camera": camera} if camera else None


def _build_sensor_payload(data, quantity_mode, selected_sensor):
    uid = data.get("uid")
    if quantity_mode == "todos":
        payload = {"uid": uid}
        for key, value in data.items():
            if key != "uid" and value is not None:
                payload[key] = value
        return payload if len(payload) > 1 else None

    sensor_data = data.get(selected_sensor)
    if sensor_data is None:
        return None

    return {selected_sensor: sensor_data, "uid": uid}


def _figure_has_mesh(figure):
    return bool(figure and getattr(figure, "data", None))


def _apply_camera(figure, camera_state):
    camera = camera_state.get("camera") if isinstance(camera_state, dict) else None
    if camera:
        figure.update_layout(scene=dict(camera=camera.copy()))


def _insert_uirevision(figure):
    figure.update_layout(scene=dict(uirevision="brain_camera"), uirevision="brain_layout")