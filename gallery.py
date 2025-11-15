import os
import json
import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from datetime import datetime

# -----------------------------
# Paths and files
# -----------------------------
PHOTOS_FOLDER = "static/photos"
COMMENTS_FILE = "data/comments.json"  # store as JSON for easy handling

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

                    html.Div(id={'type': 'status', 'index': filename}, style={"marginTop": "5px"})  # status div

                ], style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "20px"})
            )

    return html.Div([
        html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="current-user", data={"username": "Unknown"}, storage_type="session"),
        html.Div(photo_elements)
    ])

# -----------------------------
# Register gallery callbacks with status
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Output({'type': 'input', 'index': ALL}, 'value'),
        Output({'type': 'status', 'index': ALL}, 'children'),  # new status output
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        State({'type': 'input', 'index': ALL}, 'value'),
        State({'type': 'comments', 'index': ALL}, 'id'),  # get the IDs of comment divs
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def handle_comments(n_clicks_list, input_values, comment_ids, user_session):
        ctx = callback_context
        username = user_session.get("username", "Unknown User") if user_session else "Unknown User"

        comments = safe_load_comments()

        # Initialize status messages for each photo
        status_messages = [""] * len(input_values)

        triggered_id = ctx.triggered_id
        if triggered_id and triggered_id.get('type') == 'submit':
            photo_name = triggered_id['index']

            # Find input index corresponding to the submitted photo
            input_indices = [c['index'] for c in ctx.inputs_list[0]]
            input_index = input_indices.index(photo_name)
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
                    comments[photo_name].insert(0, comment_entry)  # newest on top
                    safe_save_comments(comments)

                    # Reset input box
                    input_values[input_index] = ""
                    status_messages[input_index] = dbc.Alert("Comment uploaded!", color="success", duration=3000)
                else:
                    status_messages[input_index] = dbc.Alert("Cannot submit empty comment.", color="warning", duration=3000)
            except Exception:
                status_messages[input_index] = dbc.Alert("Failed to upload comment.", color="danger", duration=3000)

        # Build comment list **in the same order as comment_ids**
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
