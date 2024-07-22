import src.py.gui.components as components
import src.py.gui.styles as styles

from dash import Dash
import dash_bootstrap_components as dbc

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.2/dbc.min.css")

app = Dash(__name__, external_stylesheets=[dbc.themes.MATERIA, dbc_css])

app.layout= components.app_layout

if __name__ =="__main__":
    app.run(debug=True)
