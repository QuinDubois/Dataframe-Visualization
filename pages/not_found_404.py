from dash import html
import dash

dash.register_page(__name__)

layout = html.H1("404: You seem to be lost, this page doesn't exist.")
