import os
from dash import html, dcc, callback_context
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
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "|" in line:
                    parts = line.strip().split("|", 3)
                    if len(parts) == 4:
                        fname, username, timestamp, text = parts
                        if fname == photo_name:
                            comments_list.append((username, timestamp, text))
    return comments_list

def save_comment(photo_name, username, comment):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(COMMENTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{photo_name}|{username}|{timestamp}|{comment.strip()}\n")

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
        dcc.Store(id="current-user", data={"username": "Unknown"}, storage_type="session"),
        html.Div(photo_elements),
    ])

# -----------------------------
# Register gallery callbacks
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Output({'type': 'input', 'index': ALL}, 'value'),
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        State({'type': 'input', 'index': ALL}, 'value'),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def handle_comments(n_clicks_list, input_values, user_session):
        ctx = callback_context

        username = user_session.get("username", "Unknown User") if user_session else "Unknown User"

        # Check if a submit button triggered this callback
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        triggered_id = eval(ctx.triggered[0]["prop_id"].split(".")[0])
        photo_name = triggered_id["index"]

        # Get index of this photo in input_values
        input_index = [i for i, comp_id in enumerate([c['index'] for c in ctx.states_list[0]]) if comp_id == photo_name][0]
        comment_text = input_values[input_index]

        # Save comment if not empty
        if comment_text and comment_text.strip():
            save_comment(photo_name, username, comment_text.strip())

        # Build comment lists for all photos
        all_comments = []
        for i, filename in enumerate(os.listdir(PHOTOS_FOLDER)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                comment_tuples = get_comments(filename)
                if comment_tuples:
                    formatted = [html.Li([html.B(f"{u} – {t}"), html.Br(), html.Span(c)]) 
                                 for (u, t, c) in comment_tuples]
                    all_comments.append(html.Ul(formatted))
                else:
                    all_comments.append(html.P("No comments yet."))

        # Reset all input boxes
        reset_inputs = [""] * len(input_values)

        return all_comments, reset_inputs
