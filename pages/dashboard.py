import dash
from dash import html, dcc, callback, Input, Output, State
import json
import numpy as np
import plotly.graph_objects as go
import pandas as pd

from resources.style_imports import STYLES, empty_chart_layout, trace_styles

from operations.plotter import plot_timeseries, plot_control
from operations.processor import aggregate_dataframe, data_sort

dash.register_page(__name__, path='/')

DATA_PATH = 'data/'
KNOWN_TEMPORAL_KEYS = ['time', 'date', 'year', 'month', 'day']

# Data Loader
########################################################################################################################
df_temperature = pd.read_csv(DATA_PATH + 'temperature.csv')
opts_temperature = []
for key in df_temperature.columns:
    if key not in KNOWN_TEMPORAL_KEYS:
        opts_temperature.append({'label': key, 'value': key})

df_data = pd.read_csv(DATA_PATH + 'data_file.csv')
opts_data = []
for key in df_data.columns:
    if key not in KNOWN_TEMPORAL_KEYS:
        opts_data.append({'label': key, 'value': key})

control_opts = []
for key in trace_styles:
    if key != 'base':
        control_opts.append({'label': key, 'value': key})
########################################################################################################################


# Dashboard layout
########################################################################################################################
layout = html.Div(className='page-container',
                  children=[
                      html.Div(
                          className='inner-container',
                          children=[

                              html.Div(id='selector-container', className='panel selector-container',
                                       children=[
                                           html.H3("Choose the dataset to use:"),
                                           dcc.Dropdown(id='dataset-selector', className='content dropdown',
                                                        options=[
                                                            {
                                                                'label': "Temperature",
                                                                'value': 'temperature'
                                                            },
                                                            {
                                                                'label': "Data File",
                                                                'value': 'data_file'
                                                            },
                                                        ],
                                                        value='data_file'
                                                        ),
                                           html.H3("Choose the data you want to plot:"),
                                           dcc.Dropdown(id='data-selector', className='content dropdown',
                                                        options=[
                                                            {
                                                                'label': "Average Temperature",
                                                                'value': 'value'
                                                            },
                                                        ],
                                                        value='value'
                                                        ),
                                           html.H3("Choose the chart type to display:"),
                                           dcc.Dropdown(id='chart-selector', className='content dropdown',
                                                        options=[
                                                            {
                                                                'label': "Temporal Chart",
                                                                'value': 'temporal'
                                                            },
                                                            {
                                                                'label': "Control Chart",
                                                                'value': 'control'
                                                            },
                                                        ],
                                                        value='temporal'
                                                        ),
                                           html.H3("Choose how you want to aggregate the data:"),
                                           dcc.Dropdown(id='aggregation-selector', className='content dropdown',
                                                        options=[
                                                            {
                                                                'label': "Mean",
                                                                'value': 'mean'
                                                            },
                                                            {
                                                                'label': "Median",
                                                                'value': 'median'
                                                            },
                                                            {
                                                                'label': "Minimum",
                                                                'value': 'min'
                                                            },
                                                            {
                                                                'label': "Maximum",
                                                                'value': 'max'
                                                            },
                                                        ],
                                                        value='mean'
                                                        ),
                                       ]),
                              html.Div(id='chart-container', className='panel chart-container',
                                       children=[
                                           html.H2(id='chart-title', children="Temporal Chart"),
                                           dcc.Graph(
                                               id="chart-content", className='content chart',
                                               figure=dict(
                                                   data=[dict(x=0, y=0)],
                                                   layout=empty_chart_layout
                                               )
                                           )
                                       ]),
                              html.Div(id='control-container', className='panel wide-panel animated-panel',
                                       children=[
                                           dcc.Checklist(id='control-checklist', className='content checklist',
                                                         options=control_opts,
                                                         value=list(trace_styles.keys())[1:]
                                                         ),
                                           dcc.Checklist(id='trend-enable', className='content checklist',
                                                         options=[{'label': "Enable all trendlines", 'value': "true"}],
                                                         value=[]
                                                         ),
                                           dcc.Slider(id='trend-slider', className='content slider',
                                                      value=10,
                                                      min=0,
                                                      max=20,
                                                      step=1,
                                                      marks={
                                                          0: {'label': '0'},
                                                          2: {'label': '2'},
                                                          4: {'label': '4'},
                                                          6: {'label': '6'},
                                                          8: {'label': '8'},
                                                          10: {'label': '10'},
                                                          12: {'label': '12'},
                                                          14: {'label': '14'},
                                                          16: {'label': '16'},
                                                          18: {'label': '18'},
                                                          20: {'label': '20'},
                                                      }
                                                      ),
                                           dcc.Slider(id='deviation-slider', className='content slider',
                                                      value=1,
                                                      min=0,
                                                      max=3,
                                                      step=1,
                                                      marks={
                                                          0: {'label': '0'},
                                                          1: {'label': '1'},
                                                          2: {'label': '2'},
                                                          3: {'label': '3'},
                                                      }
                                                      )
                                       ]),
                          ]
                      )
                  ])


########################################################################################################################


# Callbacks
########################################################################################################################

# When the chart in the dropdown changes, update the display for the chart appropriately
@callback(
    [
        Output('chart-title', 'children')
    ],
    Input('chart-selector', 'value')
)
def update_chart_title(selected_chart):
    if selected_chart == 'temporal':
        return ["Temporal Chart"]
    elif selected_chart == 'control':
        return ["Control Chart"]
    else:
        return ["Unknown Chart"]


# When the data choices change, update the chart appropriately
@callback(
    Output('chart-content', 'figure'),
    [
        Input('aggregation-selector', 'value'),
        Input('data-selector', 'value'),
        Input('dataset-selector', 'value'),
        Input('chart-selector', 'value'),
        Input('control-checklist', 'value'),
        Input('trend-enable', 'value'),
        Input('trend-slider', 'value'),
        Input('deviation-slider', 'value')
    ]
)
def update_chart_contents(
        agg_type,
        data_name,
        dataset_choice,
        chart_type,
        control_list,
        trend_toggle,
        trend_size,
        deviation_coefficient
) -> go.Figure:
    fig = go.Figure()
    df = pd.DataFrame()
    time_field = 'time'
    if dataset_choice == 'temperature':
        df = df_temperature
    elif dataset_choice == 'data_file':
        df = df_data
        time_field = 'date'

    df_by_aggregate = aggregate_dataframe(df, time_field, data_name, agg_type)

    if chart_type == 'temporal':
        fig = plot_timeseries(df_by_aggregate, 'year', data_name)
    elif chart_type == 'control':
        df_sorted, segments = data_sort(
            df_by_aggregate,
            'year',
            data_name,
            trend_size,
            deviation_coefficient,
            control_list,
            trend_toggle
        )
        fig = plot_control(df_sorted, 'year', data_name, segments, control_list, trend_toggle)

    return fig


# Change selectable data based on which dataset is chosen.
@callback(
    [
        Output('data-selector', 'options'),
        Output('data-selector', 'value')
    ],
    [
        Input('dataset-selector', 'value'),
    ]
)
def update_dropdowns(dataset_selection):
    data_select_options = []
    data_select_value = ""

    if dataset_selection == 'temperature':
        data_select_options = opts_temperature
        data_select_value = data_select_options[0]['value']
    elif dataset_selection == 'data_file':
        data_select_options = opts_data
        data_select_value = data_select_options[0]['value']

    return data_select_options, data_select_value
