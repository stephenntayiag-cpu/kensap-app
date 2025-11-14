import os
import json
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

ALUMNI_FILE = "data/alumni.json"
if not os.path.exists(ALUMNI_FILE):
    with open(ALUMNI_FILE, "w") as f:
        json.dump([], f)

def layout():
    return html.Div([
        dbc.Container([
            html.H2("KenSAP Alumni", className="text-center", style={"marginTop": "30px"}),
            html.Hr(),
            html.Div(id="alumni-list", style={"marginTop": "20px"}),
            html.Hr(),
            html.Div([
                html.H4("Add Yourself to Alumni List:"),
                dbc.Input(id="alumni-name-input", placeholder="Enter your username", type="text", style={"marginTop": "10px"}),
                dbc.Button("Add Me", id="add-alumni-button", color="primary", style={"marginTop": "10px"}),
                html.Div(id="alumni-output", style={"marginTop": "15px", "color": "green"})
            ], style={"marginTop": "30px"})
        ])
    ])

def register_callbacks(app):
    @app.callback(
        Output("alumni-list", "children"),
        Input("alumni-output", "children")
    )
    def display_alumni(_):
        with open(ALUMNI_FILE, "r") as f:
            alumni = json.load(f)
        if not alumni:
            return html.P("No alumni yet.")
        return html.Ul([html.Li(name) for name in alumni])

    @app.callback(
        Output("alumni-output", "children"),
        Input("add-alumni-button", "n_clicks"),
        State("alumni-name-input", "value")
    )
    def add_alumni(n_clicks, name):
        if not n_clicks:
            return ""
        if not name:
            return "Please enter a valid username."
        with open(ALUMNI_FILE, "r") as f:
            alumni = json.load(f)
        if name in alumni:
            return f"{name} is already in the alumni list."
        alumni.append(name)
        with open(ALUMNI_FILE, "w") as f:
            json.dump(alumni, f)
        return f"{name} has been added to the alumni list!"
