import os
import json
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import homepage
import gallery
import alumni
import profile

# Initialize app with bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
app.title = "KenSAP"
server = app.server  
USERS_FILE = "data/users.json"

# Ensure users.json exists
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# -----------------------------
# Page layouts
# -----------------------------
# FIX: user-session store MUST NOT be inside a page layout
# It must be global, not inside login_layout
login_layout = html.Div([
    dbc.Container([
        html.H2("KenSAP Login", className="text-center", style={"marginTop": "50px"}),
        dbc.Row([
            dbc.Col([
                dbc.Input(id="username", placeholder="Username", type="text", style={"marginTop": "20px"}),
                dbc.Input(id="password", placeholder="Password", type="password", style={"marginTop": "10px"}),
                dbc.Button("Login", id="login-button", color="primary", style={"marginTop": "20px"}),
                dbc.Button("Sign Up", id="signup-button", color="secondary", style={"marginTop": "10px"}),
                html.Div(id="login-output", style={"marginTop": "20px", "color": "red"}),
            ], width=6)
        ], justify="center")
    ])
])

# Layout
# FIX: global Store placed here (before any callbacks fire)
app.layout = html.Div([
    dcc.Store(id='user-session', storage_type='session'),

    dbc.NavbarSimple(
        brand="KenSAP",
        color="black",
        dark=True,
        children=[
            dbc.NavItem(dbc.NavLink("Home", href="/")),
            dbc.NavItem(dbc.NavLink("Gallery", href="/gallery")),
            dbc.NavItem(dbc.NavLink("Alumni", href="/alumni")),
            dbc.NavItem(dbc.NavLink("Profile", href="/profile")),
            dbc.NavItem(dbc.NavLink("Logout", href="/logout")),
        ]
    ),
    
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),

    html.Footer([
        html.Hr(),
        html.P(
            "© 2025 KenSAP | Designed by Stephen Ntayia",
            style={'textAlign': 'center', 'color': 'white', 'fontSize': '14px', 'marginBottom': '20px'}
        )
    ], style={
        'width': '100%',
        'backgroundColor': 'green',
        'padding': '10px 0',
        'position': 'relative',
        'bottom': '0'
    })
])

# -----------------------------
# Register callbacks
# -----------------------------
gallery.register_callbacks(app)
profile.register_callbacks(app)
alumni.register_callbacks(app)

# -----------------------------
# Page routing (FIXED)
# -----------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):

    # Login page loads FIRST
    if pathname == '/' or pathname == '/login':
        return login_layout

    elif pathname == '/gallery':
        return gallery.layout()

    elif pathname == '/alumni':
        return alumni.layout()

    elif pathname == '/profile':
        return profile.layout(session_data)

    elif pathname == '/logout':
        return html.Div("You have logged out")

    else:
        return login_layout

# -----------------------------
# Authentication callbacks
# -----------------------------
@app.callback(
    Output("login-output", "children"),
    Output("user-session", "data"),
    Input("login-button", "n_clicks"),
    Input("signup-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_auth(login_click, signup_click, username, password):
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if not username or not password:
        return "Please enter both username and password.", None

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if button_id == "login-button":
        if username in users and users[username] == password:
            return f"Login successful. Welcome {username}!", {"username": username}
        else:
            return "Invalid username or password.", None

    elif button_id == "signup-button":
        if username in users:
            return "Username already exists. Try logging in.", None
        else:
            users[username] = password
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            return f"Sign-up successful! You can now log in, {username}.", None

@app.callback(
    Output("user-session", "data"),
    Output("login-output", "children"),
    Input("url", "pathname"),
    State("user-session", "data")
)
def handle_logout(pathname, session_data):
    if pathname == "/logout":
        return None, "You have logged out."
    return session_data, dash.no_update

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
