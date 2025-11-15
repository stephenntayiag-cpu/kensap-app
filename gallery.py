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
            return []
    return comments_list

def save_comment(photo_name, username, comment):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    try:
        with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{photo_name}|{username}|{timestamp}|{comment.strip()}\n")
    except Exception:
        # Fail silently so app doesn't crash; optionally log in future
        pass

# -----------------------------
# Gallery layout
# -----------------------------
def layout():
    photo_elements = []
    photos_order = [f for f in os.listdir(PHOTOS_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    for filename in photos_order:
        photo_elements.append(
            html.Div([
                html.Img(src=f"/{PHOTOS_FOLDER}/{filename}",
                         style={"width": "300px", "margin": "10px 0"}),

                # Comments display box (appears above input)
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
        dcc.Store(id="current-user", storage_type="session"),  # username should be stored here by your login/profile logic
        html.Div(photo_elements),
        dcc.Interval(id="update-interval", interval=1500, n_intervals=0)
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
        prevent_initial_call=False
    )
    def handle_comments(n_clicks_list, n_intervals, inputs_values, user_session):
        """
        - Saves comment when the corresponding Submit button is clicked.
        - Clears only the input that was submitted.
        - Rebuilds comments display for each photo (newest comments shown on top).
        - Interval refresh keeps everyone in sync.
        """
        ctx = callback_context

        # Ensure inputs_values is a list
        if inputs_values is None:
            inputs_values = []

        # Determine username from session store (falls back to 'Unknown User')
        username = "Unknown User"
        try:
            if isinstance(user_session, dict) and user_session.get("username"):
                username = user_session.get("username")
        except Exception:
            username = "Unknown User"

        # Determine which trigger fired
        triggered_prop = None
        if ctx.triggered:
            triggered_prop = ctx.triggered[0]["prop_id"].split(".")[0]

        # Build consistent photos order (same as layout)
        photos_order = [f for f in os.listdir(PHOTOS_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

        # Default: do not change inputs (use dash.no_update)
        n_inputs = len(inputs_values)
        inputs_reset_list = [dash.no_update] * n_inputs

        # If a submit button triggered the callback, save the corresponding comment
        if triggered_prop and triggered_prop != "update-interval":
            # Parse the dict-like id string safely
            photo_name = None
            try:
                triggered_id = ast.literal_eval(triggered_prop)
                photo_name = triggered_id.get("index")
            except Exception:
                try:
                    triggered_id = eval(triggered_prop)
                    photo_name = triggered_id.get("index")
                except Exception:
                    photo_name = None

            # Find the index for this photo in photos_order
            target_index = None
            try:
                if photo_name in photos_order:
                    target_index = photos_order.index(photo_name)
            except Exception:
                target_index = None

            # If we have a target index and corresponding input value, save it
            if target_index is not None and target_index < len(inputs_values):
                comment_text = inputs_values[target_index]
                if comment_text and isinstance(comment_text, str) and comment_text.strip():
                    save_comment(photo_name, username, comment_text.strip())
                    # Clear that specific input
                    inputs_reset_list = [dash.no_update] * n_inputs
                    inputs_reset_list[target_index] = ""
        else:
            # Interval or page load triggered: do not clear inputs
            inputs_reset_list = [dash.no_update] * n_inputs

        # Rebuild comments children for each photo (in same photos_order)
        all_comments_children = []
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
                    # Empty placeholder (keeps outputs aligned)
                    all_comments_children.append(html.Div(""))
            except Exception:
                all_comments_children.append(html.Div(""))

        return all_comments_children, inputs_reset_list
