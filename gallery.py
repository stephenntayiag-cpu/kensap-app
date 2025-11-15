import os
import json
import ast
import dash
from dash import html, callback_context, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from datetime import datetime

# -----------------------------
# Paths and files
# -----------------------------
PHOTOS_FOLDER = "static/photos"
COMMENTS_FILE = "data/comments.txt"

os.makedirs(PHOTOS_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        f.write("")

# -----------------------------
# Helper functions
# -----------------------------
def get_comments(photo_name):
    comments_list = []
    if os.path.exists(COMMENTS_FILE):
        try:
            with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if "|" in line:
                        parts = line.strip().split("|", 3)
                        if len(parts) == 4:
                            fname, username, timestamp, text = parts
                            if fname == photo_name:
                                comments_list.append((username, timestamp, text))
        except Exception:
            # If file cannot be read, return empty
            return []
    return comments_list

def save_comment(photo_name, username, comment):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{photo_name}|{username}|{timestamp}|{comment.strip()}\n")
    except Exception:
        # fail silently (bulletproof): do not crash the app
        pass

# -----------------------------
# Gallery layout
# -----------------------------
def layout():
    photo_elements = []
    for filename in os.listdir(PHOTOS_FOLDER):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            photo_elements.append(
                html.Div([
                    html.Img(src=f"/{PHOTOS_FOLDER}/{filename}",
                             style={"width": "300px", "margin": "10px 0"}),

                    # Comments display box
                    html.Div(id={'type': 'comments', 'index': filename}),

                    # Comment input
                    dbc.Input(id={'type': 'input', 'index': filename},
                              placeholder="Add a comment...", type="text"),

                    # Submit button
                    dbc.Button("Submit", id={'type': 'submit', 'index': filename},
                               color="primary", n_clicks=0,
                               style={"marginTop": "5px"}),

                ], style={"border": "1px solid #ccc",
                          "padding": "10px", "marginBottom": "20px"})
            )

    return html.Div([
        html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="current-user", storage_type="session"),  # <- retrieves username
        html.Div(photo_elements),
        dcc.Interval(id="update-interval", interval=2000, n_intervals=0)
    ])

# -----------------------------
# Register gallery callbacks
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Output({'type': 'input', 'index': ALL}, 'value'),
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        Input("update-interval", "n_intervals"),
        State({'type': 'input', 'index': ALL}, 'value'),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def handle_comments(n_clicks_list, n_intervals, inputs_values, user_session):
        """
        Robust handler:
         - If submit button triggered: save corresponding comment, clear that input only.
         - If interval triggered: refresh comments only; don't clear inputs.
        Returns:
         - children for each comments div (in same order as files in PHOTOS_FOLDER)
         - list of input values matching ALL inputs (cleared for only the submitted input)
        """
        ctx = callback_context
        # Defensive defaults
        if inputs_values is None:
            inputs_values = []

        # Determine username
        username = "Unknown User"
        if user_session and isinstance(user_session, dict) and "username" in user_session:
            try:
                username = user_session.get("username") or username
            except Exception:
                pass

        triggered = None
        if ctx.triggered:
            triggered = ctx.triggered[0]["prop_id"].split(".")[0]

        # Default: do not change inputs (use dash.no_update for each)
        n_inputs = len(inputs_values)
        inputs_reset_list = [dash.no_update] * n_inputs

        # If triggered by a submit button, save the corresponding comment
        if triggered and triggered != "update-interval":
            # parse id safely
            photo_name = None
            try:
                # triggered comes as a string representation of a dict, safe-parse with ast.literal_eval
                triggered_id = ast.literal_eval(triggered)
                photo_name = triggered_id.get("index")
            except Exception:
                # fallback to eval (last resort)
                try:
                    triggered_id = eval(triggered)
                    photo_name = triggered_id.get("index")
                except Exception:
                    photo_name = None

            # Find index of this photo in the State list
            target_input_index = None
            try:
                # ctx.states_list[0] is a list of state entries for the ALL state
                state_list = ctx.states_list[0] if hasattr(ctx, "states_list") and ctx.states_list else None
                if state_list:
                    state_ids = [s['id']['index'] for s in state_list]
                    if photo_name in state_ids:
                        target_input_index = state_ids.index(photo_name)
                else:
                    # Fallback: try to match order by listing PHOTOS_FOLDER in the same manner as layout
                    photos_order = [f for f in os.listdir(PHOTOS_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
                    if photo_name in photos_order:
                        target_input_index = photos_order.index(photo_name)
            except Exception:
                target_input_index = None

            # If we found the corresponding input, read and save its value
            comment_text = None
            if target_input_index is not None and target_input_index < len(inputs_values):
                comment_text = inputs_values[target_input_index]
            # If comment present, save it
            if comment_text and isinstance(comment_text, str) and comment_text.strip():
                save_comment(photo_name, username, comment_text.strip())
                # Clear only that input on return
                inputs_reset_list = [dash.no_update] * n_inputs
                if target_input_index is not None and target_input_index < n_inputs:
                    inputs_reset_list[target_input_index] = ""
        else:
            # Interval triggered (or no trigger) -> keep inputs as-is (no clearing)
            inputs_reset_list = [dash.no_update] * n_inputs

        # Build the comments children for each photo in the same order as layout (filesystem order)
        all_comments_children = []
        photos_order = [f for f in os.listdir(PHOTOS_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        for filename in photos_order:
            try:
                comment_tuples = get_comments(filename)
                # Show newest first
                comment_tuples = list(reversed(comment_tuples))
                if comment_tuples:
                    formatted = [
                        html.Li([
                            html.B(f"{user} – {time}"),
                            html.Br(),
                            html.Span(text)
                        ]) for (user, time, text) in comment_tuples
                    ]
                    all_comments_children.append(html.Ul(formatted))
                else:
                    # keep an empty placeholder (so outputs align)
                    all_comments_children.append(html.Div(""))
            except Exception:
                all_comments_children.append(html.Div(""))

        return all_comments_children, inputs_reset_list
