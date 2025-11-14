import os
import json
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

USERS_FOLDER = "users"
if not os.path.exists(USERS_FOLDER):
    os.makedirs(USERS_FOLDER)

def layout(user_session):
    return html.Div([
        dbc.Container([
            html.H2("Your Personal Profile", className="text-center", style={"marginTop": "30px"}),
            html.Hr(),
            html.Div(id="profile-display", style={"marginTop": "20px"}),
            html.Hr(),
            html.Div([
                html.H4("Add or Update Your Info:"),
                dbc.Textarea(
                    id="profile-input",
                    placeholder="Enter your info here...",
                    style={"marginTop": "10px", "width": "100%", "height": "150px"}
                ),
                dbc.Button("Save Info", id="save-profile-button", color="primary", style={"marginTop": "10px"}),
                html.Div(id="profile-output", style={"marginTop": "15px", "color": "green"})
            ], style={"marginTop": "30px"})
        ]),
        dcc.Store(id="current-user", data=user_session, storage_type="session")
    ])

def get_profile_path(username):
    safe_username = username.replace(" ", "_")
    return os.path.join(USERS_FOLDER, f"{safe_username}.json")

def register_callbacks(app):
    @app.callback(
        Output("profile-display", "children"),
        Input("current-user", "data")
    )
    def display_profile(user_session):
        if not user_session:
            return html.P("Please log in to view your profile.")
        username = user_session.get("username")
        profile_file = get_profile_path(username)
        if not os.path.exists(profile_file):
            return html.P("No info yet. Add your info below!")
        with open(profile_file, "r") as f:
            data = json.load(f)
        return html.P(data.get("info", "No info yet."))

    @app.callback(
        Output("profile-output", "children"),
        Input("save-profile-button", "n_clicks"),
        State("profile-input", "value"),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def save_profile(n_clicks, info_text, user_session):
        if not user_session:
            return "You must be logged in to save your info."
        if not info_text:
            return "Please enter some text to save."
        username = user_session.get("username")
        profile_file = get_profile_path(username)
        with open(profile_file, "w") as f:
            json.dump({"info": info_text}, f)
        return "Your info has been saved successfully!"
