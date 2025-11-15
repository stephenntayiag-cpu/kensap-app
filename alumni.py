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
            ], style={"marginTop": "30px"}),
            # short interval to refresh the list so all users see updates quickly
            dcc.Interval(id="alumni-refresh", interval=1000, n_intervals=0)
        ])
    ])

def safe_load_alumni():
    try:
        with open(ALUMNI_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []

def safe_save_alumni(alumni):
    with open(ALUMNI_FILE, "w", encoding="utf-8") as f:
        json.dump(alumni, f, ensure_ascii=False)

def register_callbacks(app):
    @app.callback(
        Output("alumni-list", "children"),
        Input("alumni-refresh", "n_intervals")
    )
    def display_alumni(_):
        alumni = safe_load_alumni()
        if not alumni:
            return html.P("No alumni yet.")
        # Show newest on top (list is stored newest-first already)
        return html.Ul([html.Li(name) for name in alumni])

    @app.callback(
        Output("alumni-output", "children"),
        Output("alumni-name-input", "value"),
        Input("add-alumni-button", "n_clicks"),
        State("alumni-name-input", "value"),
        prevent_initial_call=True
    )
    def add_alumni(n_clicks, name):
        # Defensive checks
        if not name or not isinstance(name, str) or not name.strip():
            return "Please enter a valid username.", ""
        name = name.strip()

        alumni = safe_load_alumni()

        # Prevent duplicates (case-insensitive)
        lower_names = {a.lower() for a in alumni}
        if name.lower() in lower_names:
            return f"{name} is already in the alumni list.", ""

        # Insert newest on top
        alumni.insert(0, name)
        try:
            safe_save_alumni(alumni)
        except Exception as e:
            return f"Error saving name: {e}", ""

        # Return success message and clear input (list will refresh via Interval)
        return f"{name} has been added to the alumni list!", ""
