import os
from dash import html, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

# -----------------------------
# Paths and files
# -----------------------------
PHOTOS_FOLDER = "static/photos"
COMMENTS_FILE = "data/comments.txt"

os.makedirs(PHOTOS_FOLDER, exist_ok=True)
os.makedirs("data", exist_ok=True)

if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        f.write("")

# -----------------------------
# Helper functions
# -----------------------------
def get_comments(photo_name):
    comments_list = []
    if os.path.exists(COMMENTS_FILE):
        with open(COMMENTS_FILE, "r") as f:
            for line in f:
                if "|" in line:
                    fname, comment = line.strip().split("|", 1)
                    if fname == photo_name:
                        comments_list.append(comment)
    return comments_list

def save_comment(photo_name, comment):
    with open(COMMENTS_FILE, "a") as f:
        f.write(f"{photo_name}|{comment.strip()}\n")

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
                    dbc.Input(id={'type': 'input', 'index': filename}, placeholder="Add a comment...", type="text"),
                    dbc.Button("Submit", id={'type': 'submit', 'index': filename}, color="primary", n_clicks=0, style={"marginTop": "5px"})
                ], style={"border": "1px solid #ccc", "padding": "10px", "marginBottom": "20px"})
            )
    return html.Div([
        html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
        html.Div(photo_elements)
    ])

# -----------------------------
# Register gallery callbacks
# -----------------------------
def register_callbacks(app):
    @app.callback(
        Output({'type': 'comments', 'index': ALL}, 'children'),
        Input({'type': 'submit', 'index': ALL}, 'n_clicks'),
        State({'type': 'input', 'index': ALL}, 'value'),
        prevent_initial_call=True
    )
    def handle_comments(n_clicks_list, comments_list_state):
        ctx = callback_context
        if not ctx.triggered:
            raise dash.exceptions.PreventUpdate

        # Identify which photo was submitted
        triggered_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
        photo_name = triggered_id['index']

        # Find the corresponding input value
        input_index = next(i for i, comp_id in enumerate([c['index'] for c in ctx.inputs[1]]) if comp_id == photo_name)
        comment_text = comments_list_state[input_index]

        if comment_text and comment_text.strip():
            save_comment(photo_name, comment_text.strip())

        # Refresh all comments for all photos
        all_comments_children = []
        for filename in os.listdir(PHOTOS_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                comments = get_comments(filename)
                all_comments_children.append(html.Ul([html.Li(c) for c in comments]))
        return all_comments_children
