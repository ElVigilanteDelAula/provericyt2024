"""Callbacks simplificados para la visualización en vivo del cerebro 3D."""

import time

import plotly.graph_objects as go
from dash import Input, Output, State, ctx, no_update

from src.py.brain_viz.brain_visualizer import brain_viz
from src.py.brain_viz.simple_timeline_callbacks import register_simple_timeline_callbacks


_INTERACTION_DEFAULT = {"is_interacting": False, "last_interaction": 0.0}
_PAUSE_TRIGGER_IDS = {"timer", "memory"}


def register_brain_callbacks(app):
    """Registrar callbacks del cerebro con la aplicación Dash."""

    register_simple_timeline_callbacks(app)

    app.clientside_callback(
        """
        function(n_intervals) {
            try {
                if (typeof window.mouseTracker === 'undefined') {
                    window.mouseTracker = { isPressed: false, lastUpdate: 0 };

                    document.addEventListener('mousedown', function (event) {
                        const graphContainer = document.getElementById('brain_graph');
                        if (graphContainer && graphContainer.contains(event.target)) {
                            window.mouseTracker.isPressed = true;
                            window.mouseTracker.lastUpdate = Date.now() / 1000;
                        }
                    });

                    document.addEventListener('mouseup', function () {
                        if (window.mouseTracker.isPressed) {
                            window.mouseTracker.isPressed = false;
                            window.mouseTracker.lastUpdate = Date.now() / 1000;
                        }
                    });
                }

                return {
                    is_interacting: window.mouseTracker.isPressed,
                    last_interaction: window.mouseTracker.lastUpdate
                };
            } catch (error) {
                console.error('Mouse tracker error:', error);
                return { is_interacting: false, last_interaction: 0 };
            }
        }
        """,
        Output("brain_interaction_store", "data", allow_duplicate=True),
        Input("interaction_timer", "n_intervals"),
        prevent_initial_call=True,
    )

    @app.callback(
        Output("brain_interaction_store", "data", allow_duplicate=True),
        Input("brain_graph", "relayoutData"),
        Input("interaction_timer", "n_intervals"),
        State("brain_interaction_store", "data"),
        prevent_initial_call=True,
    )
    def detect_interaction(relayout_data, _interval, interaction_state):
        state = _merge_interaction_state(interaction_state)
        triggered_id = ctx.triggered_id if ctx.triggered else None
        now = time.time()

        if triggered_id == "brain_graph" and relayout_data:
            return {"is_interacting": True, "last_interaction": now}

        if triggered_id == "interaction_timer" and state["is_interacting"]:
            if now - state["last_interaction"] > 2.0:
                return {"is_interacting": False, "last_interaction": state["last_interaction"]}

        return state

    @app.callback(
        Output("brain_graph", "figure"),
        Output("brain_camera_store", "data"),
        Input("timer", "n_intervals"),
        Input("memory", "data"),
        Input("sensor_select", "value"),
        Input("quantity_select", "value"),
        Input("simple_timeline_mode", "data"),
        State("brain_camera_store", "data"),
        State("brain_interaction_store", "data"),
    )
    def update_brain_visualization(_, memory_data, selected_sensor, quantity_mode, timeline_state, camera_state, interaction_state):
        triggered_id = ctx.triggered_id if ctx.triggered else None
        timeline_state = timeline_state or {}
        timeline_mode = timeline_state.get("mode", "live")
        interaction_state = _merge_interaction_state(interaction_state)

        if interaction_state["is_interacting"] and triggered_id in _PAUSE_TRIGGER_IDS and timeline_mode == "live":
            return no_update, camera_state

        if timeline_mode in {"paused", "historical"} and triggered_id in _PAUSE_TRIGGER_IDS:
            return no_update, camera_state

        active_data = timeline_state.get("selected_data") if timeline_mode == "historical" else memory_data
        if not active_data or "uid" not in active_data:
            return _build_message_figure("Esperando datos de la sesión..."), camera_state

        sensors_data = _build_sensor_payload(active_data, quantity_mode, selected_sensor)
        if sensors_data is None:
            return _build_message_figure(f"No hay datos para: {selected_sensor}"), camera_state

        if len(sensors_data) <= 1:
            return _build_message_figure("No hay datos de sensores disponibles"), camera_state

        figure = brain_viz.create_live_brain_figure(sensors_data)
        _apply_timeline_title(figure, timeline_mode, timeline_state.get("selected_time"))

        camera_settings = _extract_camera(camera_state)
        if camera_settings:
            figure.update_layout(scene=dict(camera=camera_settings))

        normalized_camera = _pack_camera(camera_settings) if camera_settings else camera_state
        return figure, normalized_camera

    @app.callback(
        Output("brain_camera_store", "data", allow_duplicate=True),
        Input("brain_graph", "relayoutData"),
        State("brain_camera_store", "data"),
        prevent_initial_call=True,
    )
    def store_brain_camera_state(relayout_data, current_state):
        if not relayout_data:
            return current_state

        camera_data = relayout_data.get("scene.camera")
        if not camera_data:
            camera_data = relayout_data.get("scene", {}).get("camera") if isinstance(relayout_data.get("scene"), dict) else None

        if camera_data:
            return _pack_camera(camera_data)

        return current_state


def _merge_interaction_state(state):
    return {**_INTERACTION_DEFAULT, **(state or {})}


def _build_sensor_payload(data, quantity_mode, selected_sensor):
    uid = data.get("uid")
    payload = {"uid": uid}

    if quantity_mode == "todos":
        for key, value in data.items():
            if key != "uid" and value is not None:
                payload[key] = value
        return payload

    sensor_data = data.get(selected_sensor)
    if sensor_data is None:
        return None

    payload[selected_sensor] = sensor_data
    return payload


def _apply_timeline_title(figure, timeline_mode, selected_time):
    if not figure.layout.title:
        figure.update_layout(title="Visualización Cerebro 3D")

    base_title = figure.layout.title.text or "Visualización Cerebro 3D"
    if isinstance(base_title, str):
        base_title = base_title.split("<br><span")[0]

    if timeline_mode == "historical" and selected_time is not None:
        figure.update_layout(title=f"{base_title}<br><span style='color: orange; font-size: 12px;'>🕒 Modo Histórico: t={selected_time:.1f}s</span>")
    elif timeline_mode == "paused":
        figure.update_layout(title=f"{base_title}<br><span style='color: gray; font-size: 12px;'>⏸️ Pausado</span>")


def _build_message_figure(message):
    fig = go.Figure()
    fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16))
    fig.update_layout(template="plotly_white")
    return fig


def _extract_camera(state):
    if not state:
        return None

    if isinstance(state, dict) and "eye" in state:
        return state

    if isinstance(state, dict):
        camera = state.get("camera")
        if isinstance(camera, dict):
            return camera

    return None


def _pack_camera(camera):
    return {"camera": camera} if camera else None