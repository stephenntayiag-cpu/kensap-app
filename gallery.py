import os
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
        import json
        json.dump({}, f, ensure_ascii=False)

# -----------------------------
# Helper functions
# -----------------------------
def safe_load_comments():
    try:
        with open(COMMENTS_FILE, "r", encoding="utf-8") as f:
            import json
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}

def safe_save_comments(comments):
    try:
        with open(COMMENTS_FILE, "w", encoding="utf-8") as f:
            import json
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

                ], style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "20px"})
            )

    return html.Div([
        html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
        dcc.Store(id="current-user", data={"username": "Unknown"}, storage_type="session"),
        html.Div(photo_elements),
        # short interval to refresh comments so everyone sees updates quickly
        dcc.Interval(id="comments-refresh", interval=1000, n_intervals=0)
    ])

# -----------------------------
# Register gallery callbacks
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Output({'type': 'input', 'index': ALL}, 'value'),
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        Input("comments-refresh", "n_intervals"),
        State({'type': 'input', 'index': ALL}, 'value'),
        State("current-user", "data"),
        prevent_initial_call=True
    )
    def handle_comments(n_clicks_list, n_intervals, input_values, user_session):
        ctx = callback_context
        username = user_session.get("username", "Unknown User") if user_session else "Unknown User"

        comments = safe_load_comments()

        # Save new comment if submit button was clicked
        if ctx.triggered and ctx.triggered[0]['prop_id'].split('.')[0] != "comments-refresh":
            triggered_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
            photo_name = triggered_id['index']

            # Find input index
            input_index = [i for i, comp_id in enumerate([c['index'] for c in ctx.states_list[0]]) if comp_id == photo_name][0]
            comment_text = input_values[input_index]

            if comment_text and comment_text.strip():
                comment_entry = {"username": username, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "text": comment_text.strip()}
                if photo_name not in comments:
                    comments[photo_name] = []
                # Insert newest on top
                comments[photo_name].insert(0, comment_entry)
                safe_save_comments(comments)

        # Build comment list for all photos
        all_comments = []
        for i, filename in enumerate(os.listdir(PHOTOS_FOLDER)):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                photo_comments = comments.get(filename, [])
                if photo_comments:
                    formatted = [html.Li([html.B(f"{c['username']} – {c['timestamp']}"), html.Br(), html.Span(c['text'])])
                                 for c in photo_comments]
                    all_comments.append(html.Ul(formatted))
                else:
                    all_comments.append(html.P("No comments yet."))

        # Reset all input boxes
        reset_inputs = [""] * len(input_values)
        return all_comments, reset_inputs
