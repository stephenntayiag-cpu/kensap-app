import os
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

# Paths
PHOTOS_FOLDER = "static/photos"
COMMENTS_FILE = "data/comments.txt"

# Ensure comments file exists
if not os.path.exists(COMMENTS_FILE):
    with open(COMMENTS_FILE, "w") as f:
        f.write("")

# Helper functions
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

# Layout
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

layout = html.Div([
    html.H2("Gallery", style={"textAlign": "center", "marginTop": "20px"}),
    html.Div(photo_elements)
])

# Function to register callbacks with the app
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

        # Find which photo's submit button was clicked
        triggered_id = eval(ctx.triggered[0]['prop_id'].split('.')[0])
        photo_name = triggered_id['index']

        input_index = next(i for i, comp in enumerate(ctx.inputs_list[0]) if comp['id']['index'] == photo_name)
        comment_text = comments_list_state[input_index]

        if comment_text and comment_text.strip():
            save_comment(photo_name, comment_text.strip())

        # Refresh all comments
        all_comments_children = []
        for filename in os.listdir(PHOTOS_FOLDER):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                comments = get_comments(filename)
                all_comments_children.append(html.Ul([html.Li(c) for c in comments]))
        return all_comments_children
