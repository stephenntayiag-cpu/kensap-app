import os
import json
import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from datetime import datetime
from profile import get_current_username  # Assuming this function exists

# -----------------------------
# Paths and files
# -----------------------------
PHOTOS_FOLDER = "static/photos"
COMMENTS_FILE = "data/comments.json"

os.makedirs(PHOTOS_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False)

# -----------------------------
# Helper functions
# -----------------------------
def safe_load_comments():
    try:
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}

def safe_save_comments(comments):
    try:
        with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False)
    except Exception:
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
                    html.Img(src=f"/{PHOTOS_FOLDER}/{filename}", style={"width": "300px", "margin": "10px 0"}),

                    html.Div(id={'type': 'comments', 'index': filename}),

                    dbc.Input(id={'type': 'input', 'index': filename},
                              placeholder="Add a comment...", type="text"),

                    dbc.Button("Submit", id={'type': 'submit', 'index': filename},
                               color="primary", n_clicks=0, style={"marginTop": "5px"}),

                    dbc.Button("Show Comments", id={'type': 'show', 'index': filename},
                               color="secondary", n_clicks=0, style={"marginTop": "5px", "marginLeft": "5px"}),

                    html.Div(id={'type': 'status', 'index': filename}, style={"marginTop": "5px"})

                ], style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "20px"})
            )

    return html.Div([
        html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="current-user", data={"username": get_current_username()}, storage_type="session"),
        html.Div(photo_elements)
    ])

# -----------------------------
# Register gallery callbacks
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Output({'type': 'input', 'index': ALL}, 'value'),
        Output({'type': 'status', 'index': ALL}, 'children'),
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        Input({'type': 'show', 'index': ALL}, 'n_clicks'),  # show comments button
        State({'type': 'input', 'index': ALL}, 'value'),
        State({'type': 'comments', 'index': ALL}, 'id'),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def handle_comments(submit_n, show_n, input_values, comment_ids, user_session):
        ctx = callback_context
        username = get_current_username() if user_session.get("username") == "Unknown" else user_session.get("username")
        comments = safe_load_comments()
        status_messages = [""] * len(input_values)

        triggered_id = ctx.triggered_id

        if triggered_id:
            photo_name = triggered_id['index']
            input_indices = [comp['id']['index'] for comp in ctx.inputs_list[0]]
            input_index = input_indices.index(photo_name)

            # If submit button triggered
            if triggered_id['type'] == 'submit':
                comment_text = input_values[input_index]
                try:
                    if comment_text and comment_text.strip():
                        comment_entry = {
                            "username": username,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "text": comment_text.strip()
                        }
                        if photo_name not in comments:
                            comments[photo_name] = []
                        comments[photo_name].insert(0, comment_entry)
                        safe_save_comments(comments)
                        input_values[input_index] = ""
                        status_messages[input_index] = dbc.Alert("Comment uploaded!", color="success")
                    else:
                        status_messages[input_index] = dbc.Alert("Cannot submit empty comment.", color="warning")
                except Exception:
                    status_messages[input_index] = dbc.Alert("Failed to upload comment.", color="danger")

            # If show comments button triggered, just load existing comments
            elif triggered_id['type'] == 'show':
                status_messages[input_index] = dbc.Alert("Comments refreshed.", color="info")

        # Build comments in same order as comment_ids
        all_comments = []
        for c_id in comment_ids:
            filename = c_id['index']
            photo_comments = comments.get(filename, [])
            if photo_comments:
                formatted = [
                    html.Li([
                        html.B(f"{c['username']} – {c['timestamp']}"),
                        html.Br(),
                        html.Span(c['text'])
                    ]) for c in photo_comments
                ]
                all_comments.append(html.Ul(formatted))
            else:
                all_comments.append(html.P("No comments yet."))

        return all_comments, input_values, status_messages
