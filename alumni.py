import os
import json
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

ALUMNI_FILE = "data/alumni.json"
os.makedirs("data", exist_ok=True)
if not os.path.exists(ALUMNI_FILE):
    with open(ALUMNI_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False)

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
        Output("alumni-name-input", "value"),
        Output("alumni-output", "children"),
        Input("add-alumni-button", "n_clicks"),
        State("alumni-name-input", "value"),
        prevent_initial_call=True
    )
    def add_alumni(n_clicks, name):
        if not name or not name.strip():
            return dash.no_update, "", "Please enter a valid username."
        name = name.strip()

        # Load existing alumni
        with open(ALUMNI_FILE, "r", encoding="utf-8") as f:
            alumni = json.load(f)

        # Append new alumni if not already present
        if name not in alumni:
            alumni.insert(0, name)  # newest on top
            with open(ALUMNI_FILE, "w", encoding="utf-8") as f:
                json.dump(alumni, f, ensure_ascii=False)

        # Display updated list
        if not alumni:
            list_children = html.P("No alumni yet.")
        else:
            list_children = html.Ul([html.Li(n) for n in alumni])

        return list_children, "", f"{name} has been added to the alumni list!"
