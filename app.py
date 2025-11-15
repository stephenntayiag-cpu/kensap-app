import os
import json
import dash
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import homepage
import gallery
import alumni
import profile

# -----------------------------
# Initialize app
# -----------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
app.title = "KenSAP"
server = app.server  
USERS_FILE = "data/users.json"

# Ensure users.json exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# -----------------------------
# Page layouts
# -----------------------------
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

# -----------------------------
# App layout
# -----------------------------
app.layout = html.Div([
    dcc.Store(id='user-session', storage_type='session'),  # Global session store

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
# Register callbacks from other modules
# -----------------------------
gallery.register_callbacks(app)
profile.register_callbacks(app)
alumni.register_callbacks(app)

# -----------------------------
# Page routing
# -----------------------------
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'),
    State('user-session', 'data')
)
def display_page(pathname, session_data):
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
    elif pathname == '/homepage':
        return homepage.layout
    else:
        return login_layout

# -----------------------------
# Combined Authentication + Logout callback
# -----------------------------
@app.callback(
    Output("user-session", "data"),
    Output("login-output", "children"),
    Output("url", "pathname"),  # Redirect after login
    Input("login-button", "n_clicks"),
    Input("signup-button", "n_clicks"),
    Input("url", "pathname"),
    State("username", "value"),
    State("password", "value"),
    State("user-session", "data"),
    prevent_initial_call=True
)
def handle_auth_and_logout(login_click, signup_click, pathname, username, password, session_data):
    ctx = callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    trigger = ctx.triggered[0]['prop_id'].split('.')[0]

    # -------------------------
    # LOGOUT
    # -------------------------
    if pathname == "/logout":
        return None, "You have logged out.", "/login"

    # -------------------------
    # LOGIN / SIGNUP
    # -------------------------
    if trigger not in ["login-button", "signup-button"]:
        raise dash.exceptions.PreventUpdate

    if not username or not password:
        return session_data, "Please enter both username and password.", dash.no_update

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if trigger == "login-button":
        if username in users and users[username] == password:
            return {"username": username}, f"Login successful. Welcome {username}!", "/homepage"
        else:
            return None, "Invalid username or password.", dash.no_update

    if trigger == "signup-button":
        if username in users:
            return session_data, "Username already exists. Try logging in.", dash.no_update
        else:
            users[username] = password
            with open(USERS_FILE, "w") as f:
                json.dump(users, f)
            return session_data, f"Sign-up successful! You can now log in, {username}.", dash.no_update

# -----------------------------
# Run the app
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run_server(debug=False, host="0.0.0.0", port=port)
