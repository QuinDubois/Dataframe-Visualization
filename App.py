import dash
from dash import Dash, html

# Constants
DATA_PATH = 'data/'


# App
app = Dash(
    __name__,
    use_pages=True,
    meta_tags=[
        {'name': "viewport", 'content': "width=device-width"}
    ]
)
app.title = "Dashboard"
server = app.server

app.layout = html.Div(
    id='app-container', className='container',
    children=[
        html.Div(id='dashboard-header',
                 children=[
                     html.H1(children='Dataframe Visualization Dashboard'),
                 ]),
        dash.page_container
    ]
)


# Run the App
if __name__ == "__main__":
    app.run_server(debug=True)
