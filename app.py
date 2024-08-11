import src.py.gui.components as components
import src.py.gui.styles as styles
from src.py.database.database import Database
from src.py.utils.utils import Utils
from src.py.utils.utils import stacked_plot_factory

from dash import Dash, Input, Output, State, callback, no_update
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

db = Database(Utils.DATABASE_PATH)

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA, dbc_css])

app.layout= components.app_layout

@callback(
    Output("offcanvas", "is_open"),
    Input("open-offcanvas", "n_clicks"),
    [State("offcanvas", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open

@callback(
    Output("data_table", "data"),
    Input("refreshed_button", "n_clicks"),
)
def toggle_offcanvas(clicks):
    return db.list_sessions().to_dict("records")

@callback(
    Output("session_title", "children"),
    Output("session_notes", "children"),
    Output('line_graph', 'figure'),
    Input("data_table", "selected_row_ids"),
    Input('data_checklist','value'),
    prevent_initial_call=True
)
def set_session(selection, checked):
    return f"session_{selection[0]}", str(db.get_notes(selection[0])["notes"][0]), stacked_plot_factory(selection[0],db, checked,go.Figure())

if __name__ =="__main__":
    app.run(host="0.0.0.0", debug=True)
