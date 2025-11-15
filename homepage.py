from dash import html
import dash_bootstrap_components as dbc

def layout(session_data=None):  # <- wrap layout in a function
    return html.Div([
        dbc.Container([
            html.H1("Welcome to KenSAP", style={'textAlign': 'center', 'color': '#C0154B', 'marginTop': '30px'}),
            html.H4("Empowering Kenya’s Brightest Minds for Global Impact",
                    style={'textAlign': 'center', 'color': '#555555', 'marginBottom': '20px'}),
            dbc.Button("Learn More", color="primary", href="/gallery",
                       style={'display': 'block', 'margin': '0 auto', 'marginBottom': '40px'})
        ]),

        dbc.Container([
            html.H2("About KenSAP", style={'color': '#C0154B', 'marginTop': '20px'}),
            html.P(
                "The Kenya Scholar Access Program (KenSAP) is a non-profit initiative that identifies, prepares, "
                "and connects exceptional Kenyan students from underprivileged backgrounds with educational opportunities "
                "at some of the world’s leading universities, primarily in North America. "
                "Since its founding in 2004, KenSAP has transformed the lives of hundreds of scholars.",
                style={'fontSize': '18px', 'lineHeight': '1.8'}
            ),
        ], style={'marginBottom': '40px'}),

        dbc.Container([
            html.H2("Our Impact", style={'color': '#C0154B', 'marginTop': '20px', 'textAlign': 'center'}),
            html.P(
                "Over 320 students helped to access top universities globally.\n"
                "Alumni active in leadership, research, and entrepreneurship.\n"
                "Annual fundraising and mentoring programs to sustain opportunities.",
                style={'fontSize': '16px', 'lineHeight': '1.8', 'textAlign': 'center'}
            )
        ], style={'marginBottom': '40px'}),
    ])
