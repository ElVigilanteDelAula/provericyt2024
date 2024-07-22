from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc
import src.py.gui.styles as styles
from src.py.database.database import Database
import plotly.graph_objects as go

db = Database("test.db")
session_list = db.list_sessions()
test_events = db.get_events(20240719172230)
test_session = db.get_session(20240719172230, test_events.iloc[0, 0], test_events.iloc[-1,0])

sidebar = dbc.Stack([
    html.H1("EEG"),
    html.Hr(),
    html.Div([
        dcc.DatePickerRange(),
    ]),
    dash_table.DataTable(
        session_list.to_dict("records"),
        [{"name": i, "id": i} for i in session_list.iloc[:,[2,1]].columns],
        row_selectable="single",
        filter_action="native",
        sort_action="native",
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'width': '20vw',
        },
        page_size=6
    )
], style=styles.SIDEBAR_STYLE)

line_figure = go.Figure(
    data=[
        go.Scatter(
            x=test_session.index,
            y=test_session["attention0"],
            yaxis="y"
        ),
        go.Scatter(
            x=test_session.index,
            y=test_session["meditation0"]+100,
            yaxis="y"
        )
    ],
    layout={
        "xaxis":{
            "rangeslider":{
                "visible":True
            }
        }
    }
).add_vline(50, annotation_text="olam")


line_graph = html.Div([
    dcc.Graph(
        figure = line_figure, 
        id='line_graph',
        style=styles.GRAPH_STYLE
    )
])

graphs = dbc.Tabs([
        dbc.Tab([line_graph], label="lines")
    ],active_tab="tab-0")

main_view = html.Div([
    html.H3("session"),
    html.P("notes"),
    html.Hr(),
    graphs
],style=styles.MAIN_STYLE)

app_layout = html.Div([
    sidebar,
    main_view
], className="dbc dbc-row-selectable", style={"display":"flex"})